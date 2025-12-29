from flask import Flask, render_template, request, jsonify

from cyk import cyk_table

app = Flask(__name__)


def parse_grammar(text: str) -> dict[str, list[tuple[str, str] | str]]:
    """
    Parse grammar from text format into dict format.

    Format: "S -> A B | a" means S produces (A, B) or terminal "a"
    Each line is one non-terminal with its productions separated by |
    """
    grammar: dict[str, list[tuple[str, str] | str]] = {}

    for line in text.strip().split("\n"):
        line = line.strip()
        if not line or "->" not in line:
            continue

        lhs, rhs = line.split("->", 1)
        lhs = lhs.strip()
        productions: list[tuple[str, str] | str] = []

        for prod in rhs.split("|"):
            symbols = prod.strip().split()
            if len(symbols) == 0:
                productions.append("")  # epsilon
            elif len(symbols) == 1:
                productions.append(symbols[0])  # terminal
            elif len(symbols) == 2:
                productions.append((symbols[0], symbols[1]))  # binary rule
            else:
                raise ValueError(f"Invalid production: {prod}")

        grammar[lhs] = productions

    return grammar


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/parse", methods=["POST"])
def parse():
    data = request.get_json()
    input_str = data.get("input", "")
    grammar_text = data.get("grammar", "")
    start_symbol = data.get("start_symbol", "S")

    try:
        grammar = parse_grammar(grammar_text)
        tokens, table, accepted = cyk_table(input_str, grammar, start_symbol)

        # Convert sets to lists for JSON serialization
        table_data = [[list(cell) for cell in row] for row in table]

        return jsonify({
            "tokens": tokens,
            "table": table_data,
            "accepted": accepted,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
