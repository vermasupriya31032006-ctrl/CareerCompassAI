import matplotlib.pyplot as plt

def create_chart(scores):

    careers = list(scores.keys())
    values = list(scores.values())

    plt.figure(figsize=(8,5))
    plt.bar(careers, values)

    plt.title("Career Readiness Scores")
    plt.xlabel("Career")
    plt.ylabel("Score (%)")

    plt.tight_layout()

    chart_path = "assets/chart.png"

    plt.savefig(chart_path)

    plt.close()

    return chart_path