Chess Tournament Manager - Completed Version

How to run:

1. Open a terminal in this folder.
2. Create a virtual environment:
   python -m venv venv

3. Activate it:
   Windows:
     venv\Scripts\activate
   Mac/Linux:
     source venv/bin/activate

4. Install dependencies:
   pip install -r requirements.txt

5. Start the app:
   python app.py

6. Open this in your browser:
   http://127.0.0.1:5000

What is completed:
- Create tournaments, teams, and board players.
- Start a Swiss tournament.
- Round 1 pairs teams by seed.
- Later rounds pair teams by leaderboard order while avoiding repeat pairings when possible.
- Enter or edit every match result in a round.
- Board scores are totaled automatically.
- Match points are awarded automatically: win = 2, draw = 1, loss = 0.
- Leaderboard shows match points, board points, and Buchholz tie-break.
- Next round can only start after all current-round results are entered.
- Odd-team byes are handled automatically.