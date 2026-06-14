def find_skill_gaps(detected_skills, career_rules):

    gap_report = {}

    for career, required_skills in career_rules.items():

        missing_skills = []

        for skill in required_skills:

            if skill not in detected_skills:
                missing_skills.append(skill)

        gap_report[career] = missing_skills

    return gap_report
    