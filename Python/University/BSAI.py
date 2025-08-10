import csv
 
class BSAIData:
    def __init__(self, file=r"D:\Programming\Codes\datasets\BSAI fa 24 NCEAC Students data.csv"):
        self.file = file
            
    def read(self):
        with open(self.file) as file:
            reader = csv.DictReader(file)
            data = [{
                    "Student": row["Student Name"],
                    "Father": row["FatherName"],
                    "RollNo": int(row["RollNo"]),
                    "CNIC Number": row["CNIC Number"],
                    "Email": row["Email"],
                    "PhoneNumber": row["PhoneNumber"],
                    "Address": row["Mailing Address"],
                    "Date of Birth": row["Date of Birth"],
                } for row in reader]
            
        return data
                 
    def display(self):
        data = self.read()
        if not data:
            print("No data available.")
            return

        while True:
            choice = input("\nJust say the name: ").strip().lower()
            if choice == "exit":
                print("Exiting the search.")
                break
            
            matched_students = []
            for student in data:
                student_name = student["Student"].strip().lower()
                if choice in student_name or student_name in choice or str(student['RollNo']) == choice:
                    matched_students.append(student)
            
            if matched_students:
                print(f"\n\033[1mFound {len(matched_students)} students with matching name:\033[0m")
                print("=" * 50)
                
                for i, student in enumerate(matched_students, 1):
                    print(f"\n\033[1m{i}. Student Information:\033[0m")
                    print(f"\033[1mStudent Name:\033[0m {student['Student']}")
                    print(f"\033[1mFather Name:\033[0m {student['Father']}")
                    print(f"\033[1mRoll No:\033[0m {student['RollNo']}")
                    print(f"\033[1mCNIC Number:\033[0m {student['CNIC Number']}")
                    print(f"\033[1mEmail:\033[0m {student['Email']}")
                    print(f"\033[1mPhone Number:\033[0m {student['PhoneNumber']}")
                    print(f"\033[1mAddress:\033[0m {student['Address']}")
                    print(f"\033[1mDate of Birth:\033[0m {student['Date of Birth']}")
                    print("-" * 40)
            else:
                print(f"Student '{choice}' not found.")

    def main(self):
        print("\n\033[1mBSAI Students Information:\033[0m")
        self.display()
        
if __name__ == "__main__":
    file = BSAIData()
    file.main()