# Test runner for VPL using pytest

# Configuration

Upload `pytest_vpl.py` to your VPL assignment and ensure that it is kept while running.

Then, setup the `vpl_evaluate.sh` to contain:

```sh
cat >> vpl_execution <<EOF
python3 pytest_vpl.py tests.py
EOF
chmod +x vpl_execution
```

Ensure to change `tests.py` to the file in which your tests reside.

By default each test awards 1 point. Use `@pytest.mark.score(<int>)` to change
score given by a test.
