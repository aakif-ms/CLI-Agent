import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: agent \"your command\"")
        return
    
    user_input = sys.argv[1]
    print("User input received: ", user_input)
    
if __name__ == "__main__":
    main()