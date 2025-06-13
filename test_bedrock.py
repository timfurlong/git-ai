from git_ai import generate_pr_description

def main():
    pr_url = "https://github.com/Cloud303/cal2ts/pull/4"
    
    try:
        result = generate_pr_description(pr_url)
        print("\nGenerated PR Description:")
        print("=" * 50)
        print(result.description)
        print("=" * 50)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 