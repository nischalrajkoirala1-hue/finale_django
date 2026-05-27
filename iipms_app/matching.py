# =============================================================
# matching.py
# The intelligent matching engine.
#
# This file does one job: it takes a student and a list of
# internships, and returns each internship with a score (0-100)
# and a list of reasons explaining WHY it matched.
#
# It is kept in its own file so it is easy to improve later
# without touching the views or models.
# =============================================================


def get_match_score(student_profile, internship):
    """
    Compare one student against one internship.

    Returns a dictionary:
    {
        "score":   75,          <-- total out of 100
        "reasons": [            <-- plain-English explanations
            "Strong skill match (3 of 4 required skills matched)",
            "Industry preference matches (Technology)",
            ...
        ]
    }

    Scoring breakdown:
      - Skills match:          up to 60 points
      - Industry preference:   up to 20 points
      - Work type preference:  up to 10 points
      - Location preference:   up to 10 points
    """

    reasons = []
    total   = 0

    # ----------------------------------------------------------
    # 1. SKILL MATCH  (up to 60 points)
    # ----------------------------------------------------------
    # We compare the student's skills to the internship's skills.
    # Both are stored as comma-separated strings, e.g. "Python, SQL".
    # We convert them to lowercase sets to make comparison fair.

    student_skills_raw    = getattr(student_profile, "skills", "") or ""
    internship_skills_raw = internship.skills or ""

    student_set    = set(s.strip().lower() for s in student_skills_raw.split(",") if s.strip())
    internship_set = set(s.strip().lower() for s in internship_skills_raw.split(",") if s.strip())

    if internship_set:
        # Count how many required skills the student has
        matched_skills = student_set & internship_set
        skill_ratio    = len(matched_skills) / len(internship_set)
        skill_points   = round(skill_ratio * 60)
        total += skill_points

        if skill_points >= 48:   # 80%+ match
            reasons.append(
                f"Excellent skill match — {len(matched_skills)} of {len(internship_set)} "
                f"required skills matched ({round(skill_ratio*100)}%)"
            )
        elif skill_points >= 30:  # 50%+ match
            reasons.append(
                f"Good skill match — {len(matched_skills)} of {len(internship_set)} "
                f"required skills matched ({round(skill_ratio*100)}%)"
            )
        elif skill_points > 0:
            reasons.append(
                f"Partial skill match — only {len(matched_skills)} of {len(internship_set)} "
                f"required skills matched. Consider upskilling in: "
                f"{', '.join(internship_set - student_set)}"
            )
        else:
            reasons.append(
                "No matching skills found. Required: "
                + (", ".join(internship_set) if internship_set else "none listed")
            )
    else:
        # Internship has no skills listed — give partial credit
        total += 30
        reasons.append("No specific skills required for this internship")

    # ----------------------------------------------------------
    # 2. INDUSTRY PREFERENCE  (up to 20 points)
    # ----------------------------------------------------------

    student_industry = getattr(student_profile, "industry_pref", "") or ""
    job_industry     = internship.industry or ""

    if student_industry in ("Any", "No preference", ""):
        # Student has no preference — give them half credit
        total += 10
        reasons.append("No industry preference set — all industries considered equally")
    elif job_industry == "":
        # Internship has no industry listed — neutral
        total += 10
        reasons.append("No industry specified for this internship")
    elif student_industry.lower() == job_industry.lower():
        total += 20
        reasons.append(f"Industry preference matches ({job_industry})")
    else:
        reasons.append(
            f"Industry mismatch — you prefer {student_industry}, "
            f"this role is in {job_industry}"
        )

    # ----------------------------------------------------------
    # 3. WORK TYPE PREFERENCE  (up to 10 points)
    # ----------------------------------------------------------

    student_work = getattr(student_profile, "work_type", "") or ""
    job_work     = internship.work_type or ""

    if student_work in ("Any", "No preference", ""):
        total += 10
        reasons.append("Open to any work type")
    elif job_work == "":
        total += 5
        reasons.append("Work type not specified for this internship")
    elif student_work.lower() == job_work.lower():
        total += 10
        reasons.append(f"Work type matches ({job_work})")
    else:
        reasons.append(
            f"Work type mismatch — you prefer {student_work}, "
            f"this role is {job_work}"
        )

    # ----------------------------------------------------------
    # 4. LOCATION PREFERENCE  (up to 10 points)
    # ----------------------------------------------------------

    student_loc = getattr(student_profile, "location_pref", "") or ""
    job_loc     = internship.location or ""

    if not student_loc:
        total += 5
        reasons.append("No location preference set")
    elif not job_loc:
        total += 5
        reasons.append("No location specified for this internship")
    else:
        s_lower = student_loc.lower()
        j_lower = job_loc.lower()

        # Remote jobs match any location preference
        if "remote" in j_lower or "remote" in s_lower:
            total += 10
            reasons.append("Remote position — matches any location preference")
        elif s_lower in j_lower or j_lower in s_lower:
            total += 10
            reasons.append(f"Location matches your preference ({job_loc})")
        else:
            reasons.append(
                f"Location may not match — you prefer {student_loc}, "
                f"this role is in {job_loc}"
            )

    # ----------------------------------------------------------
    # Cap score between 0 and 100
    # ----------------------------------------------------------
    total = max(0, min(100, total))

    return {
        "score":      total,
        "reasons":    reasons,
        "internship": internship,
    }


def rank_internships_for_student(student_profile, internships):
    """
    Score every internship for this student and return them
    sorted from highest score to lowest.

    Parameters:
        student_profile  -- StudentProfile object
        internships      -- QuerySet or list of Internship objects

    Returns:
        A list of dicts, each like:
        { "score": 75, "reasons": [...], "internship": <Internship> }
    """

    results = []

    for job in internships:
        result = get_match_score(student_profile, job)
        results.append(result)

    # Sort highest score first
    results.sort(key=lambda r: r["score"], reverse=True)

    return results
