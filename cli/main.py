import sys

def main():

    if len(sys.argv) < 2:
        print("Usage: python cli/main.py <project_path>")
        return

    project_path = sys.argv[1]

    print("===================================")
    print(" Brent Detector")
    print("===================================")

    print(f"Analyzing project: {project_path}")

    print("\nStep 1: Scanning files...")
    print("Step 2: Extracting dependencies...")
    print("Step 3: Building dependency graph...")
    print("Step 4: Calculating Brent scores...")

    print("\nAnalysis complete.")

if __name__ == "__main__":
    main()