import os
import requests

USERNAME = "ASHUTOSH_KUMAR_06"
URL = "https://leetcode.com/graphql"

def fetch_data():
    query = """
    query userContestRankingInfo($username: String!) {
        userContestRanking(username: $username) {
            attendedContestsCount
            rating
            globalRanking
            topPercentage
        }
        userContestRankingHistory(username: $username) {
            attended
            rating
            contest {
                title
                startTime
            }
        }
        matchedUser(username: $username) {
            submitStats {
                acSubmissionNum {
                    difficulty
                    count
                }
            }
        }
    }
    """
    response = requests.post(URL, json={"query": query, "variables": {"username": USERNAME}})
    return response.json()["data"]

def generate_svg(data):
    ranking_info = data["userContestRanking"]
    history = data["userContestRankingHistory"]
    stats = data["matchedUser"]["submitStats"]["acSubmissionNum"]
    
    # Filter attended contests
    attended = [h for h in history if h["attended"]]
    if not attended:
        return "" # fallback
    
    # Extract ratings
    ratings = [h["rating"] for h in attended]
    min_rating = min(ratings)
    max_rating = max(ratings)
    
    current_rating = int(ranking_info["rating"])
    top_percent = ranking_info["topPercentage"]
    global_rank = ranking_info["globalRanking"]
    
    total_solved = next((s["count"] for s in stats if s["difficulty"] == "All"), 0)
    
    # SVG Configuration
    width = 500
    height = 200
    padding_x = 40
    padding_y = 70
    graph_width = width - 2 * padding_x
    graph_height = height - padding_y - 30
    
    # Map points
    points = []
    if len(ratings) > 1:
        x_step = graph_width / (len(ratings) - 1)
        rating_range = max(max_rating - min_rating, 1) # avoid div by zero
        for i, r in enumerate(ratings):
            x = padding_x + i * x_step
            y = height - 30 - ((r - min_rating) / rating_range) * graph_height
            points.append(f"{x},{y}")
    else:
        points = [f"{padding_x},{height/2}"]
        
    polyline_points = " ".join(points)
    
    # Estimate path length for animation
    path_length = int(graph_width * 1.5)
    
    # SVG Template
    svg = f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
    <style>
        .title {{ font: 600 16px 'Segoe UI', Ubuntu, Sans-Serif; fill: #c9d1d9; }}
        .stat {{ font: 400 12px 'Segoe UI', Ubuntu, Sans-Serif; fill: #8b949e; }}
        .val {{ font: 600 14px 'Segoe UI', Ubuntu, Sans-Serif; fill: #6C63FF; }}
        .graph-line {{
            stroke-dasharray: {path_length};
            stroke-dashoffset: {path_length};
            animation: draw 2s ease-in-out forwards;
        }}
        .fade-in {{
            opacity: 0;
            animation: fadeIn 1s ease-in-out 1.5s forwards;
        }}
        @keyframes draw {{
            to {{ stroke-dashoffset: 0; }}
        }}
        @keyframes fadeIn {{
            to {{ opacity: 1; }}
        }}
    </style>
    
    <rect width="{width}" height="{height}" rx="15" fill="#0d1117" stroke="#30363d"/>
    
    <!-- Header -->
    <text x="25" y="35" class="title">🏆 LeetCode Contest Rating</text>
    
    <!-- Stats -->
    <text x="25" y="65" class="stat">Rating: <tspan class="val">{current_rating}</tspan></text>
    <text x="140" y="65" class="stat">Top: <tspan class="val">{top_percent}%</tspan></text>
    <text x="240" y="65" class="stat">Global Rank: <tspan class="val">{global_rank}</tspan></text>
    <text x="380" y="65" class="stat">Solved: <tspan class="val">{total_solved}</tspan></text>
    
    <!-- Graph Grid -->
    <line x1="{padding_x}" y1="{height - 30}" x2="{width - padding_x}" y2="{height - 30}" stroke="#30363d" stroke-dasharray="4"/>
    
    <!-- Graph -->
    <polyline points="{polyline_points}" fill="none" stroke="#6C63FF" stroke-width="2" class="graph-line"/>
    
    <!-- Data Points (Fade in after line draws) -->
    <g class="fade-in">
    """
    
    for pt in points:
        x, y = pt.split(",")
        svg += f'<circle cx="{x}" cy="{y}" r="3" fill="#FF6347" />\n'
        
    svg += """
    </g>
    </svg>
    """
    return svg

if __name__ == "__main__":
    os.makedirs("assets", exist_ok=True)
    data = fetch_data()
    svg_content = generate_svg(data)
    with open("assets/leetcode-animated.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
