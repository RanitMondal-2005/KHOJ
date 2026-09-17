"""
matching/engine.py

Rule-Based Matching Engine for Khoj
=====================================
Compares a MissingPerson against an UnidentifiedPatient
and returns a confidence score (0-100) with a per-field breakdown.

TWO HARD FILTERS run before any scoring:
  1. Gender  — MALE<->MALE, FEMALE<->FEMALE, OTHER<->OTHER only.
  2. Date    — Patient admitted BEFORE missing date = impossible. Eliminated without any scoring.

SCORING BREAKDOWN (exactly 100 pts total):
-------------------------------------------
  Face similarity (dlib)       - up to 30 pts
  Identifying marks (Jaccard)  - up to 15 pts
  Age similarity               - up to 15 pts
  Height similarity            - up to 12 pts
  Clothing overlap (Jaccard)   - up to 10 pts
  Blood group                  -      5 pts
  District                     -      5 pts
  Weight similarity            - up to 4 pts
  Skin tone                    -      2 pts
  Eye color                    -      1 pt
  Hair color                   -      1 pt
--------------------------------------------
  Total                        -    100 pts

"""

from django.conf import settings


# ── HARD FILTERS ─────────────────────────────────────────────────────────────

def should_compare(missing, patient):
    """
    Two hard filters before any scoring runs.
    Returns False = skip this pair entirely (logical impossibility).
    Returns True  = proceed to full scoring.
    """

    # filter 1 — strict gender match
    if missing.gender != patient.gender:
        return False

    # filter 2 — date impossibility check
    if patient.admission_date < missing.last_seen_date:
        return False

    return True


# ── FACE RECOGNITION (dlib) ───────────────────────────────────────────────────

def score_face_similarity(missing, patient):
    """
    dlib is an open-source, C++ toolkit with Python bindings designed for machine learning and computer vision. In our project, it handles the end-to-end facial recognition pipeline.
    - Compares 2 photos : missing.passport_photo (family uploaded) with patient.face_image (hospital uploaded) using dlib's face recognition model.

    How dlib face recognition works:
      1. Detection (HOG Detector) : dlib detects human faces in both images.
      2. Landmark Alignment : shape_predictor_68_face_landmarks finds 68 facial landmarks (i.e, locates the exact (x, y) coordinates of key anatomical features like
         eyes, nose, mouth corners, jawlines etc.) on each detected face.
      3. Feature Extraction (ResNet Embedding): dlib_face_recognition_resnet_model_v1 passes the aligned face through a pre-trained ResNet neural network to convert the image into a 128d vector array.
            - WHAT IS 128d VECTOR?
                Instead of comparing millions of raw pixels of an image, dlib's ResNet converts the face's
                unique geometric features (eye spacing, nose shape, jawline curve) into a list(array)
                of 128 distinct float numbers. eg : [-0.1402, 0.0823, 0.0541, -0.0912, ..., 0.0489]..
                Two photos of the same person produce nearly identical 128 numbers, allowing
                instant identity matching via basic vector subtraction (Euclidean distance).
      4. Euclidean Distance Comparison of Two Image : calculates the geometric distance between the two 128d vector arrays. Decison taken based on this distance.
      5. Returns 0 silently on any failure related to face matching:
            - Never crashes the matching engine.
    """
    import os # will be used to interact with the system files directly

    # 1. Database check: Verify image fields are populated in the database records
    if not missing.passport_photo or not patient.face_image:
        return 0

    mp_path = missing.passport_photo.path # NOTE : .path comes directly from Django's ImageField / FileField to give the actual location path of that specific file in the server
    pt_path = patient.face_image.path

    # 2. Filesystem check: Verify physical files actually exist on hard disk before passing to dlib
    if not os.path.exists(mp_path) or not os.path.exists(pt_path):
        return 0

    try:
        import dlib
        import numpy as np
        # --------------------  STEP 1 : FIND LOCATION of Models --------------------
        """
         Load dlib's pre-trained weights via face_recognition_models.
         Since dlib's core runs locally on the host machine, it requires direct filesystem
         paths to open these files. Instead of hardcoding static paths (which break
         across different servers or systems), these helpers
         dynamically resolve the exact absolute locations of the model files wherever pip installed them.
        """
        import face_recognition_models
        predictor_path = face_recognition_models.pose_predictor_model_location()  # 1. Finds where the 68-landmark model file sits & Returns the file's address as a text string
        face_rec_model_path = face_recognition_models.face_recognition_model_location() # 2. Finds where the ResNet face recognition model file sits & Returns the file's address as a text string

        # --------------------  STEP 2 : INITIALIZE dlib tools with those locations --------------------
        detector  = dlib.get_frontal_face_detector()        # 1. HOG face detector
        predictor = dlib.shape_predictor(predictor_path)    # 2. 68 landmark finder
        face_rec  = dlib.face_recognition_model_v1(face_rec_model_path)  # 3. ResNet encoder

        # -------------------------- STEP 3 : ACTUAL PROCESS OF DLIB (Detection -> Alignment(68 Landmarks) -> 128-d Embedding) --------------------------
        def get_face_encoding(image_path):
            """
            Helper: loads an image, detects the primary face, and extracts its
            128-dimensional biometric embedding(vectors). Returns None if no face is found.
            """
            img = dlib.load_rgb_image(image_path)

            # STEP 3.1 : detect faces in the image —> returns list of bounding boxes eg: [rectangle(left, top, right, bottom)]...
            detections = detector(img, 1)  # The 1 parameter (Upsampling): Tells dlib to double the size of the image once before scanning. This increases resolution, allowing the detector to spot smaller or slightly distant faces that would otherwise be missed.

            if len(detections) == 0:
                # no human face found in this image, so back
                return None

            # STEP 3.2 :  Facial Alignment (68 Landmarks)
            shape    = predictor(img, detections[0])  # Use the first detected face to find 68 landmarks

            # STEP 3.3 : 128-d Embedding
            encoding = face_rec.compute_face_descriptor(img, shape)  # Passes the raw image alongside the 68 alignment landmarks into a 29-layer ResNet neural network. As The Output: The neural network transforms the normalized face into a mathematical fingerprint consisting of 128 floating-point numbers in an array.

            # STEP 3.4 : A raw dlib.vector does not support standard mathematical operations in Python; so we convert it to a NumPy array.
            return np.array(encoding)

        # get face encodings for both photos
        enc_missing = get_face_encoding(mp_path) # for Family Side
        enc_patient = get_face_encoding(pt_path) # for Hospital Side

        # if either photo has no detectable face — can't compare
        if enc_missing is None or enc_patient is None:
            return 0

        # Calculate euclidean distance between two 128-d face vectors
        distance = np.linalg.norm(enc_missing - enc_patient) # numpy.linalg.norm() computes a vector norm (Euclidean Distance btw two 128d Vector array); it compares index 0 with index 0, index 1 with index 1, all the way to index 127 and then returns one single number (a float), not an array.

        # convert distance to score
        if distance <= 0.3:    return 30   # very strong match
        elif distance <= 0.45: return 22   # strong match
        elif distance <= 0.6:  return 14   # may be possible match
        else:                  return 0    # likely different people

    except Exception:
        # never crash the matching engine due to face recognition failure — silently return 0
        return 0


# ── TEXT SIMILARITY HELPER ────────────────────────────────────────────────────

def _keyword_overlap(text1, text2, max_score):
    """
    Jaccard similarity on keyword sets extracted from two text fields.

    Algorithm:
      1. Lowercase both texts
      2. Replace commas with spaces, split into word tokens
      3. Remove stopwords that carry no meaning (on, in, the, left, right etc.)
      4. Jaccard ratio = |common words| / |union of words|
      5. Score = ratio * max_score

    Example:
      text1 = "scar on left forehead, tattoo on wrist"
      text2 = "forehead scar, small tattoo"
      After stopword removal: {scar, forehead, tattoo, wrist} vs {forehead, scar, small, tattoo}
      Common = {scar, forehead, tattoo} = 3
      Union  = {scar, forehead, tattoo, wrist, small} = 5
      Ratio  = 3/5 = 0.6 -> intersection/union will always produce a value btw 0 to 1 then we will normalize it
      Score  = 0.6 * 15 = 9 pts

    Used for both identifying_marks and clothing_description fields.
    """
    if not text1 or not text2:
        return 0

    # stopwords that appear frequently but add no identifying value
    stopwords = {
        'on', 'in', 'the', 'a', 'an', 'of', 'at', 'and', 'or',
        'with', 'near', 'left', 'right', 'upper', 'lower', 'small',
        'large', 'old', 'worn', 'color', 'colour', 'side', 'has', 'have'
    }

    # Applying the Alogorthm
    words1 = set(text1.lower().replace(',', ' ').split()) - stopwords # Minus Stop word, means : remove these stop words from our cleaned words1
    words2 = set(text2.lower().replace(',', ' ').split()) - stopwords

    if not words1 or not words2:
        return 0

    common = words1.intersection(words2)
    union  = words1.union(words2)

    if not union:
        return 0

    return round((len(common) / len(union)) * max_score, 1)


# ── INDIVIDUAL SCORING FUNCTIONS ──────────────────────────────────────────────

def score_identifying_marks(missing, patient):
    """
    Jaccard keyword overlap on identifying marks. Max 15 pts.
    """
    return _keyword_overlap(
        missing.identifying_marks,
        patient.identifying_marks,
        max_score=15
    )


def score_age(missing, patient):
    """
    Age similarity with partial credit for close estimates.
      ±3 yrs  - 15 pts  (very close)
      ±6 yrs  - 10 pts  (close — within estimation margin)
      ±10 yrs -  5 pts  (rough match)
      >10 yrs -  0 pts  (too different)
    """
    diff = abs(missing.age - patient.age)
    if diff <= 3:   return 15
    if diff <= 6:   return 10
    if diff <= 10:  return 5
    return 0


def score_height(missing, patient):
    """
    Height similarity in cm. Max 12 pts.
    Height is fixed in adults — biologically reliable.
      ±5 cm  - 12 pts
      ±10 cm -  8 pts
      ±15 cm -  4 pts
      >15 cm -  0 pts
    """
    diff = abs(missing.height - patient.height)
    if diff <= 5:   return 12
    if diff <= 10:  return 8
    if diff <= 15:  return 4
    return 0


def score_clothing(missing, patient):
    """
    Jaccard keyword overlap on clothing description. Max 10 pts.
    """
    return _keyword_overlap(
        missing.clothing_description,
        patient.clothing_description,
        max_score=10
    )


def score_blood_group(missing, patient):
    """
    Exact blood group match — 5 pts.
    UNKNOWN on either side - 0 (can't compare).
    """
    mp = missing.blood_group.upper()
    pt = patient.blood_group.upper()
    if 'UNKNOWN' in (mp, pt):
        return 0
    return 5 if mp == pt else 0


def score_district(missing, patient):
    """
    Same district = 5 pts. Spatial context only.
    - district alone is weak evidence because people can travel across districts before being found.
    """
    mp = missing.district.strip().lower()
    pt = patient.district.strip().lower()
    return 5 if mp == pt else 0


def score_weight(missing, patient):
    """
    Weight similarity in kg. Max 4 pts.
    Low weight because weight fluctuates & not very reliable.
      ±5 kg  - 4 pts
      ±10 kg - 2 pts
      >10 kg - 0 pts
    """
    diff = abs(missing.weight - patient.weight)
    if diff <= 5:   return 4
    if diff <= 10:  return 2
    return 0


def score_skin_tone(missing, patient):
    """
    2 pts for skin tone match.
    Low weight — skin tone assessment is affected by:
    hospital lighting conditions, camera quality, skin conditions etc.
    """
    mp = missing.skin_tone.upper()
    pt = patient.skin_tone.upper()
    if 'UNKNOWN' in (mp, pt):
        return 0
    return 2 if mp == pt else 0


def score_eye_color(missing, patient):
    """
    1 pt for eye color match.
    Low weight — very low variance in Indian population.
    """
    if not missing.eye_color or not patient.eye_color:
        return 0
    return 1 if missing.eye_color.strip().lower() == patient.eye_color.strip().lower() else 0


def score_hair_color(missing, patient):
    """
    1 pt for hair color match.
    Low weight — hair can be dyed, shaved, dirty, or altered.
    """
    if not missing.hair_color or not patient.hair_color:
        return 0
    return 1 if missing.hair_color.strip().lower() == patient.hair_color.strip().lower() else 0


# ── MAIN SCORING FUNCTION ─────────────────────────────────────────────────────

def compute_match_score(missing_person, unidentified_patient):
    """
    Runs all 11 scoring functions and returns:
      - total score: float, capped at 100.0
      - breakdown: dictionary with each factor's individual score

    The breakdown dict is stored as JSONField on MatchResult —
    templates use it to show exactly which fields contributed.

    Gender and date are NOT in breakdown — they are hard filters
    that already ran in should_compare() before this is called.
    """
    breakdown = {
        'face_match':  score_face_similarity(missing_person, unidentified_patient),
        'marks':       score_identifying_marks(missing_person, unidentified_patient),
        'age':         score_age(missing_person, unidentified_patient),
        'height':      score_height(missing_person, unidentified_patient),
        'clothing':    score_clothing(missing_person, unidentified_patient),
        'blood_group': score_blood_group(missing_person, unidentified_patient),
        'district':    score_district(missing_person, unidentified_patient),
        'weight':      score_weight(missing_person, unidentified_patient),
        'skin_tone':   score_skin_tone(missing_person, unidentified_patient),
        'eye_color':   score_eye_color(missing_person, unidentified_patient),
        'hair_color':  score_hair_color(missing_person, unidentified_patient),
    }

    total = round(min(sum(breakdown.values()), 100.0), 1)
    return total, breakdown


# ── MATCH RUNNERS ─────────────────────────────────────────────────────────────

def run_matching_for_missing_person(missing_person):
    """
    Called by Django signal when a MissingPerson record is saved by a Family.
    Compares against ALL UNIDENTIFIED patients in the database.

    Flow:
      1. Fetch all UNIDENTIFIED patients
      2. For each patient — run should_compare() hard filters first
         (gender filter + date filter)
      3. If filters pass — run compute_match_score()
      4. If score >= threshold — store/update MatchResult

    get_or_create prevents duplicates (unique_together on model).
    If match already exists and score changed — update it.
    """
    from hospital.models import UnidentifiedPatient
    from matching.models import MatchResult

    threshold = getattr(settings, 'MATCH_CONFIDENCE_THRESHOLD', 40)
    patients = UnidentifiedPatient.objects.filter(status='UNIDENTIFIED')

    for patient in patients:

        # hard filters run first — skip impossible pairs before scoring
        if not should_compare(missing_person, patient):
            continue

        score, breakdown = compute_match_score(missing_person, patient)

        if score >= threshold:
            match, created = MatchResult.objects.get_or_create( # get_or_create() method always returns a tuple containing two items: (object, created) ; object->MatchResult & created ->True/False (always)
                missing_person=missing_person,
                unidentified_patient=patient,
                defaults={
                    'confidence_score': score,
                    'score_breakdown': breakdown,
                    'status': 'PENDING'
                }
            )
            # If created is False, the record already existed -> update score if it changed on re-run
            if not created and match.confidence_score != score:
                match.confidence_score = score # Set old number to new number
                match.score_breakdown = breakdown # Update BreakDown Dict
                match.save()


def run_matching_for_patient(unidentified_patient):
    """
    Called by Django signal when an UnidentifiedPatient record is saved by Hospital.
    Compares against ALL ACTIVE missing person reports.

    Same FLOW as run_matching_for_missing_person but from patient side.
    """
    from family.models import MissingPerson
    from matching.models import MatchResult

    threshold = getattr(settings, 'MATCH_CONFIDENCE_THRESHOLD', 40)
    missing_cases = MissingPerson.objects.filter(status='ACTIVE')

    for missing in missing_cases:

        # hard filters first — eliminate impossible pairs
        if not should_compare(missing, unidentified_patient):
            continue

        score, breakdown = compute_match_score(missing, unidentified_patient)

        if score >= threshold:
            match, created = MatchResult.objects.get_or_create(
                missing_person=missing,
                unidentified_patient=unidentified_patient,
                defaults={
                    'confidence_score': score,
                    'score_breakdown': breakdown,
                    'status': 'PENDING'
                }
            )
            if not created and match.confidence_score != score:
                match.confidence_score = score
                match.score_breakdown = breakdown
                match.save()

