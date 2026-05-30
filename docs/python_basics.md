# Python Basics

## Variables

Python me variables banane ke liye koi type declare nahi karna padta. Bas naam likho aur value de do:

```python
name = "Wajid"
age = 25
is_learning = True
```

Python ko khud pata chal jaata hai ki ye string hai, integer hai, ya boolean.

## Data Types

Python ke main data types:

- **int** — whole numbers (5, -3, 1000)
- **float** — decimal numbers (3.14, -0.5)
- **str** — text ("hello", 'bhai')
- **bool** — True ya False
- **list** — ordered, changeable: [1, 2, 3]
- **tuple** — ordered, NOT changeable: (1, 2, 3)
- **dict** — key-value pairs: {"name": "Wajid"}
- **set** — unique values: {1, 2, 3}

## Functions

Function ek reusable code block hai. Define karne ke liye `def` use karte hain:

```python
def greet(name):
    return f"Hello, {name}!"

print(greet("Wajid"))  # Output: Hello, Wajid!
```

Function arguments le sakta hai aur `return` se value wapas de sakta hai. Agar return nahi hai to None return hota hai.

## Lists

List ordered collection hai. Items change kar sakte ho:

```python
fruits = ["apple", "banana", "mango"]
fruits.append("orange")    # add at end
fruits[0] = "grapes"        # change first item
print(len(fruits))           # 4
```

## Loops

`for` loop kisi bhi iterable pe chalta hai:

```python
for fruit in fruits:
    print(fruit)

for i in range(5):  # 0 se 4 tak
    print(i)
```

`while` loop condition true rehne tak chalta hai:

```python
count = 0
while count < 3:
    print(count)
    count += 1
```

## Dictionaries

Key-value pairs. Lookup O(1) hota hai:

```python
person = {"name": "Wajid", "city": "Delhi", "age": 25}
print(person["name"])       # Wajid
person["job"] = "developer"  # add new key
```

## Error Handling

Errors handle karne ke liye try-except use karo:

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")
except Exception as e:
    print(f"Some error: {e}")
```
