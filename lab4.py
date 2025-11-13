import tkinter as tk
from tkinter import messagebox

BASES = {
    2: "Бинарная (2)",
    8: "Восьмеричная (8)",
    10: "Десятичная (10)",
    16: "Шестнадцатеричная (16)",
}


def convert_int_to_base(value: int, base: int) -> str:
    if value == 0:
        return "0"
    digits = "0123456789ABCDEF"
    negative = value < 0
    value = abs(value)
    result = []
    while value > 0:
        value, remainder = divmod(value, base)
        result.append(digits[remainder])
    converted = "".join(reversed(result))
    return f"-{converted}" if negative else converted


def parse_value(text: str, base: int) -> int:
    try:
        return int(text, base)
    except ValueError as exc:
        raise ValueError(
            f"Не удалось преобразовать значение '{text}' из системы счисления с основанием {base}."
        ) from exc


def calculate(operation: str, a_text: str, b_text: str, base_a: int, base_b: int):
    a = parse_value(a_text, base_a)
    b = parse_value(b_text, base_b)

    if operation == "+":
        return a + b
    if operation == "-":
        return a - b
    if operation == "*":
        return a * b
    if operation == "/":
        if b == 0:
            raise ZeroDivisionError("Деление на ноль невозможно")
        return a / b
    raise ValueError("Неизвестная операция")


def show_result(result_label: tk.Label, result):
    if isinstance(result, int):
        lines = ["Результат:"]
        for base in BASES:
            converted = convert_int_to_base(result, base)
            lines.append(f"{BASES[base]}: {converted}")
        result_label.config(text="\n".join(lines))
    else:
        text = (
            "Результат (десятичный): "
            + (f"{result:.10g}" if isinstance(result, float) else str(result))
            + "\nПеревод в другие системы доступен только для целых чисел."
        )
        result_label.config(text=text)


def on_calculate(result_label: tk.Label, entry_a: tk.Entry, entry_b: tk.Entry,
                 base_var_a: tk.IntVar, base_var_b: tk.IntVar, operation_var: tk.StringVar):
    try:
        result = calculate(
            operation_var.get(),
            entry_a.get().strip(),
            entry_b.get().strip(),
            base_var_a.get(),
            base_var_b.get(),
        )
    except ZeroDivisionError as error:
        messagebox.showerror("Ошибка", str(error))
        return
    except ValueError as error:
        messagebox.showerror("Ошибка", str(error))
        return

    show_result(result_label, result)


def on_convert(entry: tk.Entry, source_base_var: tk.IntVar,
               target_base_var: tk.IntVar, result_label: tk.Label):
    try:
        value = parse_value(entry.get().strip(), source_base_var.get())
    except ValueError as error:
        messagebox.showerror("Ошибка", str(error))
        return

    converted = convert_int_to_base(value, target_base_var.get())
    result_label.config(
        text=(
            "Перевод:\n"
            f"Исходная система {BASES[source_base_var.get()]}: {entry.get().strip()}\n"
            f"Целевая система {BASES[target_base_var.get()]}: {converted}"
        )
    )


def create_interface():
    root = tk.Tk()
    root.title("Калькулятор систем счисления")
    root.resizable(False, False)

    base_var_a = tk.IntVar(value=10)
    base_var_b = tk.IntVar(value=10)
    convert_source_var = tk.IntVar(value=10)
    target_base_var = tk.IntVar(value=2)
    operation_var = tk.StringVar(value="+")

    frame_inputs = tk.LabelFrame(root, text="Арифметика")
    frame_inputs.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    tk.Label(frame_inputs, text="Число A:").grid(row=0, column=0, sticky="w")
    entry_a = tk.Entry(frame_inputs, width=25)
    entry_a.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_inputs, text="Система A:").grid(row=0, column=2, sticky="w")
    option_a = tk.OptionMenu(frame_inputs, base_var_a, *BASES.keys())
    option_a.grid(row=0, column=3, padx=5)

    tk.Label(frame_inputs, text="Число B:").grid(row=1, column=0, sticky="w")
    entry_b = tk.Entry(frame_inputs, width=25)
    entry_b.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(frame_inputs, text="Система B:").grid(row=1, column=2, sticky="w")
    option_b = tk.OptionMenu(frame_inputs, base_var_b, *BASES.keys())
    option_b.grid(row=1, column=3, padx=5)

    tk.Label(frame_inputs, text="Операция:").grid(row=2, column=0, sticky="w")
    operation_menu = tk.OptionMenu(frame_inputs, operation_var, "+", "-", "*", "/")
    operation_menu.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    result_label = tk.Label(root, text="Результат будет показан здесь", justify="left")
    result_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

    tk.Button(
        frame_inputs,
        text="Вычислить",
        command=lambda: on_calculate(
            result_label, entry_a, entry_b, base_var_a, base_var_b, operation_var
        ),
    ).grid(row=2, column=2, columnspan=2, padx=5, pady=5)

    frame_convert = tk.LabelFrame(root, text="Перевод числа")
    frame_convert.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

    tk.Label(frame_convert, text="Число:").grid(row=0, column=0, sticky="w")
    entry_convert = tk.Entry(frame_convert, width=25)
    entry_convert.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_convert, text="Исходная система:").grid(row=0, column=2, sticky="w")
    option_source = tk.OptionMenu(frame_convert, convert_source_var, *BASES.keys())
    option_source.grid(row=0, column=3, padx=5)

    tk.Label(frame_convert, text="Целевая система:").grid(row=1, column=0, sticky="w")
    option_target = tk.OptionMenu(frame_convert, target_base_var, *BASES.keys())
    option_target.grid(row=1, column=1, padx=5)

    tk.Button(
        frame_convert,
        text="Преобразовать",
        command=lambda: on_convert(entry_convert, convert_source_var, target_base_var, result_label),
    ).grid(row=1, column=2, columnspan=2, padx=5, pady=5)

    root.mainloop()


if __name__ == "__main__":
    create_interface()
