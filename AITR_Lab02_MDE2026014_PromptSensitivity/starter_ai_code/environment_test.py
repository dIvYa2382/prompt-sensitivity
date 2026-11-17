import sys
print("Python:", sys.version)

try:
    import pandas as pd
    import numpy as np
    print("pandas:", pd.__version__)
    print("numpy:", np.__version__)
    test = pd.DataFrame({"item_id": ["pilot_01"], "prompt_variant": ["A"]})
    assert test.shape == (1, 2)
    print("Environment smoke test: PASS")
except Exception as exc:
    print("Environment smoke test: FAIL")
    raise

