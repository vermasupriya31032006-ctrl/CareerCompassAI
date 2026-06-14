def calculate_scores(detected_skills, career_rules):

    scores = {}

    for career, required_skills in career_rules.items():

        matched = 0

        total = len(required_skills)

        for skill in required_skills:

            if skill in detected_skills:
                matched += 1

        score = int((matched / total) * 100)

        scores[career] = score

    return scores