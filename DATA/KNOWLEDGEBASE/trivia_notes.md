# Trivia Handler Notes

## Source
- API: [Open Trivia Database](https://opentdb.com/) — free, no key required
- Encoding: `url3986` (percent-encoded) to avoid JSON special-character issues

## Supported Categories
| Keyword     | OpenTDB ID |
|-------------|------------|
| general     | 9          |
| science     | 17         |
| history     | 23         |
| geography   | 22         |
| sports      | 21         |
| music       | 12         |
| movies      | 11         |
| computers   | 18         |

## Cache
- Stored at `DATA/trivia_cache.json`
- TTL: **1 hour** (3600 seconds)
- Falls back to stale cache if the API is unreachable

## Usage Examples
```python
from tools.trivia_handler import get_random_question, format_question

q = get_random_question(category="science")
print(format_question(q))
```

## Integration Notes
- `format_question` shuffles answer choices on every call
- The correct answer is always appended in the formatted output for JARVIS to read aloud
- Extend `CATEGORY_MAP` to add more OpenTDB categories as needed
