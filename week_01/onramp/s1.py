name = "Zobayer"
base = 160_000          # underscores are just readable separators
growth = 0.25
print(f"{name} targets {base * (1 + growth):,.0f} next year")


skills = ["SQL", "Power BI", "DAX", "Python", "Claude API"]
print(skills[0], skills[-1])   # first, last
print(skills[1:3])             # slice: index 1 up to (not including) 3
skills.append("DuckDB")
print(len(skills), skills)