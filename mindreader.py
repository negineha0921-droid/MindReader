
import random
import json

def load_scores():
    try:
        with open("highscores.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"1": None, "2": None, "3": None}

def save_scores(scores):
    with open("highscores.json", "w") as f:
        json.dump(scores, f)

def play_game(max_attempts, max_number):

    secret = random.randint(1, max_number)
    attempts = 0

    print("\nGuess the number between 1 and", max_number)
    print("You have", max_attempts, "attempts.")

    while attempts < max_attempts:
        try:
            guess = int(input("Enter your guess: "))
        except ValueError:
            print("Please enter a number.")
            continue

        if guess < 1 or guess > max_number:
            print("Please enter a number between 1 and", max_number)
            continue

        attempts += 1

        if guess < secret:
            print("Higher!")
            print("Attempts left:", max_attempts - attempts)

        elif guess > secret:
            print("Lower!")
            print("Attempts left:", max_attempts - attempts)

        else:
            print("You read my mind!")
            print("You guessed it in", attempts, "attempts")
            return attempts

    else:
        print("Game over! You are out of attempts.")
        print("The correct number was:", secret)

    return None


# Welcome message
print("Welcome to My Mindreader Game!")
print("Let's guess the number.")

# Store best scores for each level
best_scores = load_scores()

while True:

    # Select difficulty level
    print("\nChoose your difficulty level:")
    print("1. Easy")
    print("2. Medium")
    print("3. Hard")

    level = input("Enter your choice (1/2/3): ")

    if level == "1":
        print("\nYou selected EASY level!")
        score = play_game(max_attempts=10, max_number=50)

    elif level == "2":
        print("\nYou selected MEDIUM level!")
        score = play_game(max_attempts=7, max_number=100)

    elif level == "3":
        print("\nYou selected HARD level!")
        score = play_game(max_attempts=9, max_number=500)

    else:
        print("Invalid level choice!")
        continue

    # High score feature
    if score is not None:
        if best_scores[level] is None or score < best_scores[level]:
            best_scores[level] = score
            save_scores(best_scores) 
            print("New best score for this level:", score)
        else:
            print("Best score for this level:", best_scores[level])

    # Play again feature
    while True:
        play_again = input("\nDo you want to play again? (Y/N): ").upper()

        if play_again == "Y" or play_again == "N":
            break

        print("Please type Y or N.")

    if play_again == "N":
        print("Thank you for playing Mindreader Game!")
        break
