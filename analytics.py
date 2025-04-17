# analytics.py

import statistics

class GameAnalytics:
    def __init__(self):
        self.scores = []
        self.health_snapshots = []

    def record_score(self, score):
        self.scores.append(score)

    def record_health(self, health):
        self.health_snapshots.append(health)

    def get_analytics(self):
        if not self.scores:
            return {}
        
        return {
            'count': len(self.scores),
            'mean': round(statistics.mean(self.scores), 2),
            'median': statistics.median(self.scores),
            'mode': statistics.mode(self.scores) if len(set(self.scores)) < len(self.scores) else 'No mode',
            'min': min(self.scores),
            'max': max(self.scores),
            'range': max(self.scores) - min(self.scores)
        }

    def print_analytics(self):
        analytics = self.get_analytics()
        if not analytics:
            print("No analytics data yet.")
            return

        print("\n===== Game Analytics =====")
        for k, v in analytics.items():
            print(f"{k.title()}: {v}")
        print("==========================\n")
