use std::collections::HashMap;
use pyo3::{prelude::*, IntoPyObjectExt};

/// Formats the sum of two numbers as string.
#[pyfunction]
fn count_words(py: Python, s: String) -> Py<PyAny>{
    let mut hm: HashMap<char, usize> = HashMap::new();

    for word in s.chars() {
        let count = hm.entry(word).or_insert(0);

        *count += 1;
    }
    hm.into_py_any(py).unwrap()
}

/// A Python module implemented in Rust.
#[pymodule]
fn test_mod(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(count_words, m)?)?;
    Ok(())
}
