"""
The Heart of Our KHOJ Project :-
Rule-Based Matching Engine for Khoj Logic :
Compares a MissingPerson report against an UnidentifiedPatient record
and returns both a total confidence score AND a per-field breakdown dict.

Scoring Breakdown (Total possible = 110, capped at 100):
---------------------------------------------------------
  Gender exact match           → +20
  Blood group exact match      → +15
  Age similarity               → up to +15
  Height similarity            → up to +10
  District match               → +10
  Identifying marks overlap    → up to +10
  Clothing overlap             → up to +10
  Face photo similarity        → up to +10  (face_recognition library)
  Weight similarity            → up to +5
  Eye color match              → +5
  Hair color match             → +5
  Skin tone match              → +5
---------------------------------------------------------
  TOTAL MAX (capped)           = 100

Threshold: only store matches >= MATCH_CONFIDENCE_THRESHOLD (default 40)

# Each function compares one aspect of the missing person and patient data,
# returning a score based on how closely they match.
 MATCHING ALGORITHM LOGIC ->
 1. Exact matches get full points.
 2. Similarities (like age, height) get partial points.
 3. UNKNOWN values are treated as non-matches.
and this are done by individual scoring functions via fixed scoring logic(RULES).
Also, the total score is capped at 100. Although individual aspects may score higher, the final match score will not exceed this cap.
Logic of this Cap : The scoring functions are designed to return a maximum score for each aspect, and the overall match score is calculated by summing these individual scores. If the total exceeds 100, it is capped at 100.

"""

from django.conf import settings   # importing Django settings file


# ── individual scoring functions ──────────────────────────────────────────────

def score_gender(missing, patient):   # function to compare gender
    """20 pts for exact gender match. 0 if either is UNKNOWN."""
    
    mp = missing.gender.upper()   # convert missing person's gender to uppercase
    pt = patient.gender.upper()   # convert patient's gender to uppercase

    if 'UNKNOWN' in (mp, pt):     # if any gender is UNKNOWN
        return 0                  # no score given

    return 20 if mp == pt else 0  # return 20 if both genders match otherwise 0


def score_blood_group(missing, patient):   # function to compare blood group
    """15 pts for exact blood group match. 0 if UNKNOWN on either side."""

    mp = missing.blood_group.upper()   # convert missing person's blood group to uppercase
    pt = patient.blood_group.upper()   # convert patient's blood group to uppercase

    if 'UNKNOWN' in (mp, pt):          # if any blood group is UNKNOWN
        return 0                       # no score

    return 15 if mp == pt else 0       # exact match gives 15 otherwise 0


def score_age(missing, patient):   # function to compare age similarity
    """
    Age similarity with partial credit:
      ±3 yrs  → 15 pts
      ±6 yrs  → 10 pts
      ±10 yrs →  5 pts
      >10 yrs →  0 pts
    """

    diff = abs(missing.age - patient.age)   # calculate absolute age difference

    if diff <= 3:   return 15   # very close age
    if diff <= 6:   return 10   # moderately close age
    if diff <= 10:  return 5    # slight age similarity

    return 0                    # too much difference


def score_height(missing, patient):   # function to compare height
    """
    Height similarity in cm:
      ±5 cm  → 10 pts
      ±10 cm →  6 pts
      ±15 cm →  3 pts
      >15 cm →  0 pts
    """

    diff = abs(missing.height - patient.height)   # calculate height difference

    if diff <= 5:   return 10   # almost same height
    if diff <= 10:  return 6    # close height
    if diff <= 15:  return 3    # slight similarity

    return 0                    # very different height


def score_weight(missing, patient):   # function to compare weight
    """
    Weight similarity in kg:
      ±5 kg  → 5 pts
      ±10 kg → 3 pts
      >10 kg → 0 pts
    """

    diff = abs(missing.weight - patient.weight)   # calculate weight difference

    if diff <= 5:   return 5    # close weight
    if diff <= 10:  return 3    # somewhat similar weight

    return 0                    # weight too different


def score_district(missing, patient):   # function to compare district
    """10 pts if same district (case-insensitive). Geographic anchor."""

    mp = missing.district.strip().lower()   # remove spaces and convert to lowercase
    pt = patient.district.strip().lower()   # remove spaces and convert to lowercase

    return 10 if mp == pt else 0            # same district gives 10 otherwise 0


def score_eye_color(missing, patient):   # function to compare eye color
    """5 pts for exact eye color match."""

    if not missing.eye_color or not patient.eye_color:   # if any eye color missing
        return 0                                         # no score

    return 5 if missing.eye_color.strip().lower() == patient.eye_color.strip().lower() else 0
    # exact eye color match gives 5


def score_hair_color(missing, patient):   # function to compare hair color
    """5 pts for exact hair color match."""

    if not missing.hair_color or not patient.hair_color:   # if any hair color missing
        return 0                                           # no score

    return 5 if missing.hair_color.strip().lower() == patient.hair_color.strip().lower() else 0
    # exact hair color match gives 5


def score_skin_tone(missing, patient):   # function to compare skin tone
    """5 pts for skin tone match. 0 if UNKNOWN."""

    mp = missing.skin_tone.upper()   # convert missing person's skin tone to uppercase
    pt = patient.skin_tone.upper()   # convert patient's skin tone to uppercase

    if 'UNKNOWN' in (mp, pt):        # if any value is UNKNOWN
        return 0                     # no score

    return 5 if mp == pt else 0      # exact match gives 5


def _keyword_overlap_score(text1, text2, max_score):   # helper function for text similarity
    """
    Shared helper: keyword overlap between two text fields.
    Lowercases, splits into words, removes stopwords,
    then scores based on Jaccard overlap ratio.
    Used for both identifying_marks and clothing_description.
    """

    if not text1 or not text2:   # if any text is empty
        return 0                 # no score

    stopwords = {                # common words to ignore
        'on', 'in', 'the', 'a', 'an', 'of', 'at', 'and', 'or',
        'with', 'near', 'left', 'right', 'upper', 'lower', 'small',
        'large', 'old', 'worn', 'color', 'colour'
    }

    words1 = set(text1.lower().replace(',', ' ').split()) - stopwords
    # convert first text into lowercase keyword set

    words2 = set(text2.lower().replace(',', ' ').split()) - stopwords
    # convert second text into lowercase keyword set

    if not words1 or not words2:   # if no useful words remain
        return 0                   # no score

    common = words1.intersection(words2)   # find common keywords
    union  = words1.union(words2)          # find all unique keywords

    if not union:   # safety check
        return 0

    return round((len(common) / len(union)) * max_score, 1)
    # Jaccard similarity formula × max score


def score_identifying_marks(missing, patient):   # compare identifying marks
    """Keyword overlap on identifying marks text. Max 10 pts."""

    return _keyword_overlap_score(
        missing.identifying_marks,    # missing person's marks
        patient.identifying_marks,    # patient's marks
        max_score=10                  # maximum possible score
    )


def score_clothing(missing, patient):   # compare clothing description
    """Keyword overlap on clothing description. Max 10 pts."""

    patient_clothing = getattr(patient, 'clothing_description', '') or ''
    # safely get patient clothing description

    missing_clothing = missing.clothing_description or ''
    # get missing person's clothing description

    return _keyword_overlap_score(missing_clothing, patient_clothing, max_score=10)
    # calculate overlap score


def score_face_similarity(missing, patient):   # compare photos
    """
    Compares the missing person's passport photo with the patient's face image
    using perceptual hashing (imagehash library).

    How perceptual hashing works:
      - Each image is converted into a compact hash based on its visual structure
      - Similar-looking images produce similar hashes
      - The 'distance' between hashes tells us how visually different they are
      - Distance 0 = identical images, higher = more different

    This is NOT facial recognition. It detects visual similarity between photos.
    Works well when the same person's photo is uploaded from different angles
    or with slight lighting differences.

    Scoring:
      distance 0      → 10 pts
      distance 1-5    → 7 pts
      distance 6-10   → 4 pts
      distance 11-15  → 1 pt
      distance > 15   → 0 pts

    Returns 0 silently if photos are missing or anything fails.
    Never crashes the matching engine.
    """

    import os   # importing os module for file checking

    if not missing.passport_photo or not patient.face_image:
        return 0   # return 0 if any photo missing

    mp_path = missing.passport_photo.path   # path of missing person's photo
    pt_path = patient.face_image.path       # path of patient's face image

    if not os.path.exists(mp_path) or not os.path.exists(pt_path):
        return 0   # return 0 if files not found

    try:
        import imagehash           # library for perceptual hashing
        from PIL import Image      # image processing library

        hash1 = imagehash.phash(Image.open(mp_path))
        # generate perceptual hash for missing person's image

        hash2 = imagehash.phash(Image.open(pt_path))
        # generate perceptual hash for patient image

        distance = hash1 - hash2
        # calculate hash distance between images

        if distance == 0:      return 10   # identical images
        elif distance <= 5:    return 7    # very similar images
        elif distance <= 10:   return 4    # somewhat similar
        elif distance <= 15:   return 1    # slight similarity
        else:                  return 0    # too different

    except Exception:
        return 0   # silently fail if any image error happens


# ── main scoring function ─────────────────────────────────────────────────────

def compute_match_score(missing_person, unidentified_patient): # for calculating overall match score between a missing person and an unidentified patient
    """
    Runs all scoring checks and returns:
      - total confidence score (float, capped at 100)
      - breakdown dict showing each factor's individual score

    The breakdown dict is stored in MatchResult.score_breakdown (JSONField)
    so templates can display exactly which fields contributed.

    Returns:
        tuple: (total_score: float, breakdown: dict)
    """

    breakdown = {
        'gender':      score_gender(missing_person, unidentified_patient),      # gender score
        'blood_group': score_blood_group(missing_person, unidentified_patient), # blood group score
        'age':         score_age(missing_person, unidentified_patient),         # age score
        'height':      score_height(missing_person, unidentified_patient),      # height score
        'weight':      score_weight(missing_person, unidentified_patient),      # weight score
        'district':    score_district(missing_person, unidentified_patient),    # district score
        'eye_color':   score_eye_color(missing_person, unidentified_patient),   # eye color score
        'hair_color':  score_hair_color(missing_person, unidentified_patient),  # hair color score
        'skin_tone':   score_skin_tone(missing_person, unidentified_patient),   # skin tone score
        'marks':       score_identifying_marks(missing_person, unidentified_patient), # marks score
        'clothing':    score_clothing(missing_person, unidentified_patient),    # clothing score
        'face_match':  score_face_similarity(missing_person, unidentified_patient), # face similarity score
    }

    total = round(min(sum(breakdown.values()), 100.0), 1)
    # add all scores, cap maximum at 100, round to 1 decimal

    return total, breakdown   # return total score and detailed breakdown


# ── match runners ─────────────────────────────────────────────────────────────

def run_matching_for_missing_person(missing_person):
    """
    Triggered when a new MissingPerson is saved (via signal).
    Compares against all UNIDENTIFIED patients and stores matches above threshold.
    """

    from hospital.models import UnidentifiedPatient   # import patient model
    from matching.models import MatchResult           # import match result model

    threshold = getattr(settings, 'MATCH_CONFIDENCE_THRESHOLD', 40)
    # get threshold value from settings, default = 40

    patients = UnidentifiedPatient.objects.filter(status='UNIDENTIFIED')
    # fetch all unidentified patients

    for patient in patients:   # loop through every patient

        score, breakdown = compute_match_score(missing_person, patient)
        # calculate score between missing person and patient

        if score >= threshold:   # only save strong matches

            match, created = MatchResult.objects.get_or_create(
                missing_person=missing_person,      # current missing person
                unidentified_patient=patient,       # current patient

                defaults={
                    'confidence_score': score,      # save total score
                    'score_breakdown': breakdown,  # save breakdown dictionary
                    'status': 'PENDING'            # default match status
                }
            )

            if not created and match.confidence_score != score:
                # if match already exists but score changed

                match.confidence_score = score      # update score
                match.score_breakdown = breakdown   # update breakdown

                match.save()   # save updated match


def run_matching_for_patient(unidentified_patient):
    """
    Triggered when a new UnidentifiedPatient is saved (via signal).
    Compares against all ACTIVE missing person reports.
    """

    from family.models import MissingPerson   # import missing person model
    from matching.models import MatchResult   # import match result model

    threshold = getattr(settings, 'MATCH_CONFIDENCE_THRESHOLD', 40)
    # get threshold from settings

    missing_cases = MissingPerson.objects.filter(status='ACTIVE')
    # fetch all active missing person reports

    for missing in missing_cases:   # loop through every missing case

        score, breakdown = compute_match_score(missing, unidentified_patient)
        # calculate matching score

        if score >= threshold:   # only store meaningful matches i.e. those with a high confidence score

            match, created = MatchResult.objects.get_or_create(
                missing_person=missing,                 # current missing person
                unidentified_patient=unidentified_patient, # current patient

                defaults={
                    'confidence_score': score,      # store confidence score
                    'score_breakdown': breakdown,  # store detailed breakdown
                    'status': 'PENDING'            # default status
                }
            )

            if not created and match.confidence_score != score:
                # if match exists and score changed, when the new score is higher
                # than the old score for a new search 

                match.confidence_score = score      # update score on existing match
                match.score_breakdown = breakdown   # update breakdown for existing match

                match.save()   # save updated result