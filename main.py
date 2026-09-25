from agent import run_agent


def main():

    print("======================================")
    print("            SHOPPING AGENT            ")
    print("======================================")

    print("\nAvailable roles:")
    print("1. customer")
    print("2. admin")

    role = input("\nEnter your role: ").strip().lower()

    if role not in {"customer", "admin"}:
        print("Invalid role. Using customer.")
        role = "customer"

    print(f"\nLogged in as: {role}")
    print("Type 'exit' to quit.")

    while True:

        user_request = input("\nYou: ").strip()

        if user_request.lower() == "exit":
            print("Goodbye!")
            break

        if not user_request:
            print("Please enter a request.")
            continue

        if len(user_request) < 2:
            print("Please enter a more specific request.")
            continue

        try:
            result = run_agent(
                user_request=user_request,
                role=role,
            )

            print("\nAgent:")
            print(result["answer"])

        except Exception as error:

            print("\nApplication Error:")
            print(
                "The application could not "
                "complete the request safely."
            )

            print(f"Debug: {error}")


if __name__ == "__main__":
    main()
