import os

filepath = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\gs1\gs1_pwonlyias.md"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Define target content and replacement content
target = """### Answer

| **Core Demand of the Question** <br>• Political relevance of French Revolution <br>• Social relevance of French Revolution <br>• Economic relevance of French Revolution <br>• Global relevance of French Revolution |
| --- |

The **French Revolution (1789)** was a watershed event in world history that not only transformed France but also had a profound and lasting impact on the global political, social, and economic landscape. Its core principles of **liberty, equality,** and **fraternity** became the foundation for modern democratic societies, and its relevance continues to be felt in contemporary times.

**Political Relevance**
- **Rise of Democracy:** The Revolution challenged the divine right of kings and asserted the sovereignty of the people.

  - **Eg:** France’s 1791 Constitution established a constitutional monarchy and later a republic, inspiring Europe-wide democratic movements.

- **Legal Equality:** It abolished feudal privileges and created uniform laws.

  - **Eg:** The **Napoleonic Code (1804)** influenced legal systems in Italy, Spain, Latin America, and even modern civil law traditions worldwide.

- **Popular Sovereignty:** Introduced the idea that legitimacy flows from citizens, not monarchs.

  - **Eg:** It Inspired the **Revolutions of 1848** and later movements in Asia and Africa.

**Social Relevance**
- **Social Equality:** Ended aristocratic and clerical privileges.

  - **Eg:** The Abolition of feudal dues (1789) broke landlord dominance over peasants.

- **Women’s Rights Debate:** Sparked early feminist thought which eventually led to status of equality for women.

  - **Eg:** Olympe de Gouges’s “Declaration of the Rights of Woman” (1791):** demanded gender equality.

- **Mass Participation:** Peasants and commoners became political actors, inspiring later grassroots movements.
- **Cultural Impact:** Revolutionary art, festivals, and symbols (Tricolour, Marseillaise) remain potent emblems of freedom.

**Economic Relevance**
- **Abolition of Feudal Economy:** Feudal dues and manorial rights were abolished.
- **Redistribution of Land:** Confiscated church lands were sold, creating a new class of small peasant proprietors.
- **Uniform Taxation:** Ended tax exemptions for nobility and clergy.

  - **Eg:** Taille and tithe abolished:** , ensuring equality before revenue laws.

- **Rise of Bourgeoisie:** The Middle classes gained prominence in trade, commerce, and administration, foreshadowing modern capitalism.
- **State-led Economic Policies:** Revolutionary government undertook price controls, abolished internal tariffs, and promoted free trade in agriculture.

**Global Relevance**
- **Inspiration for Revolutions:** It sparked revolts worldwide. The **Haitian Revolution (1791–1804)** drew on French revolutionary ideals.
- **Spread of Nationalism:** Ideas of self-determination influenced anti-colonial struggles.

  - **Eg:** The **Indian freedom movement** and leaders like Rammohan Roy admired its ideals.

- **Human Rights Framework:** Inspired the modern charters like the **UN Universal Declaration of Human Rights (1948)**.
- **Republicanism as a Global Norm:** Shift from monarchy to republican governance across Europe, Asia, and Latin America.
- **Challenge to Imperialism:** Supported liberation movements in colonies, leaving a lasting anti-colonial legacy."""

replacement = """### Answer

| **Core Demand of the Question** <br>• Political relevance of French Revolution <br>• Social relevance of French Revolution <br>• Economic relevance of French Revolution <br>• Global relevance of French Revolution |
| --- |

The **French Revolution (1789)** was a watershed event in world history that not only transformed France but also had a profound and lasting impact on the global political, social, and economic landscape. Its core principles of **liberty, equality,** and **fraternity** became the foundation for modern democratic societies, and its relevance continues to be felt in contemporary times.

**Political Relevance**
- **Rise of Democracy:** The Revolution challenged the divine right of kings and asserted the sovereignty of the people.
  - **Eg:** France’s 1791 Constitution established a constitutional monarchy and later a republic, inspiring Europe-wide democratic movements.
- **Legal Equality:** It abolished feudal privileges and created uniform laws.
  - **Eg:** The **Napoleonic Code (1804)** influenced legal systems in Italy, Spain, Latin America, and even modern civil law traditions worldwide.
- **Popular Sovereignty:** Introduced the idea that legitimacy flows from citizens, not monarchs.
  - **Eg:** It Inspired the **Revolutions of 1848** and later movements in Asia and Africa.

**Social Relevance**
- **Social Equality:** Ended aristocratic and clerical privileges.
  - **Eg:** The Abolition of feudal dues (1789) broke landlord dominance over peasants.
- **Women’s Rights Debate:** Sparked early feminist thought which eventually led to status of equality for women.
  - **Eg:** Olympe de Gouges’s “Declaration of the Rights of Woman” (1791) demanded gender equality.
- **Mass Participation:** Peasants and commoners became political actors, inspiring later grassroots movements.
- **Cultural Impact:** Revolutionary art, festivals, and symbols (Tricolour, Marseillaise) remain potent emblems of freedom.

**Economic Relevance**
- **Abolition of Feudal Economy:** Feudal dues and manorial rights were abolished.
- **Redistribution of Land:** Confiscated church lands were sold, creating a new class of small peasant proprietors.
- **Uniform Taxation:** Ended tax exemptions for nobility and clergy.
  - **Eg:** Taille and tithe abolished, ensuring equality before revenue laws.
- **Rise of Bourgeoisie:** The Middle classes gained prominence in trade, commerce, and administration, foreshadowing modern capitalism.
- **State-led Economic Policies:** Revolutionary government undertook price controls, abolished internal tariffs, and promoted free trade in agriculture.

**Global Relevance**
- **Inspiration for Revolutions:** It sparked revolts worldwide. The **Haitian Revolution (1791–1804)** drew on French revolutionary ideals.
- **Spread of Nationalism:** Ideas of self-determination influenced anti-colonial struggles.
  - **Eg:** The **Indian freedom movement** and leaders like Rammohan Roy admired its ideals.
- **Human Rights Framework:** Inspired the modern charters like the **UN Universal Declaration of Human Rights (1948)**.
- **Republicanism as a Global Norm:** Shift from monarchy to republican governance across Europe, Asia, and Latin America.
- **Challenge to Imperialism:** Supported liberation movements in colonies, leaving a lasting anti-colonial legacy."""

# Check if target matches exactly (ignoring newline difference if any, but let's do normal replace)
# To handle potential windows line endings
target_normalized = target.replace("\r\n", "\n")
content_normalized = content.replace("\r\n", "\n")

if target_normalized in content_normalized:
    new_content = content_normalized.replace(target_normalized, replacement)
    # Write back
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_content)
    print("Success: Replaced content perfectly!")
else:
    # Try a substring match to find where it mismatches
    print("Error: Target content not found exactly in the file.")
    # Let's print a small chunk of both to debug
    print("Target starts with:")
    print(target_normalized[:100])
