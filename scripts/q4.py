# This script is used for evaluating question 4, it will automatically get the code block and output the amount of tests passed.

ns2 = {"response": response}

exec(response.split("```python")[-1].split("```")[0], ns2)
exec("""
tests = {
    "192.168.1.1": True, "0.0.0.0": True, "255.255.255.255": True,
    "256.1.1.1": False, "01.1.1.1": False, "1.1.1": False,
    "1.1.1.1.": False, " 1.1.1.1": False, "1.1.1.a": False,
    "": False, "1..1.1": False, "+1.1.1.1": False,
}
passed = sum(is_valid_ipv4(k) == v for k, v in tests.items())
print(f"{passed}/12")
""", ns2)