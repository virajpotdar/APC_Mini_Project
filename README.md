1. About the Project
-It is a simple Python GUI application that helps friends manage expenses during a trip.
It records who paid for an expense and helps calculate how much each person should contribute.

2. Main Features
- Create and manage a trip.
- Add friends to the trip.
- Add trip expenses.
- View each friend's contribution and balance.
- Calculate who should pay whom.
- Generate a simple expense report.
- View expense charts if the required library is installed.
- Delete a selected expense.
- Delete the entire trip after confirmation.
  
3. Technologies Used
- Python: Main programming language.
- Tkinter: Creates the graphical user interface (GUI).
- JSON, CSV, and text files: Store trip and report data.
- Matplotlib, NumPy

4. How It Works
- Open the application.
- Enter the trip name and budget, if required.
- Add the names of friends.
- Enter each expense and select the person who paid.
- View the balances and settlement suggestions.
- Save or generate a report when needed.
   
* Simple Example
Three friends—Viraj, Rahul, and Amit—share a total expense of ₹900.
₹900 ÷ 3 = ₹300 per person.
If Viraj paid the full ₹900, Rahul and Amit each owe Viraj ₹300.

5. How to Run
- Install the required/optional libraries if needed:
   pip install -r requirements.txt
- Start the GUI:
   python launch_gui.py
   If launch_gui.py not working then start main.py 

6. Conclusion
TripSplit makes it easier to record shared trip expenses, check each friend's balance, and work out who needs to pay whom. It is a small project for learning Python, GUI programming, file handling, and basic data processing.
