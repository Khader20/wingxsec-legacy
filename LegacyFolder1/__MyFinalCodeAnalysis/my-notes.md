# My Final Code Analysis
This document contains my final analysis of the current codebase.
I will write my thoughts and observations here, as they come to mind.
Also, I will use simple language as thoughts come out naturally of my mind.

---

- I see that the code is very bad-structured.
- I have made multiple folders under the name `cross_section_properties{i}` to test different things.
- The naming conventions are inconsistent, which makes it hard to follow.
- Anyway, this was a initial attempt to achieve the goals.

- the code is not modular at all !
- the code contains folders with empty files, which should be removed. such as `structural_model`, since we are focusing on wing 2d cross-section properties computations & analysis.


---
# The best test code that works are : (at the root of the project)
- `Wing_Full_FE_AeroElas_SourceCode\test_cross_3.py`
    - 🧪 it tests a case with a closed wing section.
    - ✅ good userflow.
    - ✅ it uses `sectionproperties` to compute the cross-section properties, which is a good library for this purpose.
    - ❌ But, it has the "warping" issue for closed wing sections, which is not good.
    ``` terminal
    UserWarning: 
    The section geometry contains disjoint regions which is invalid for warping analysis.
    Please revise your geometry to ensure there is connectivity between all regions.
    Please see https://sectionproperties.rtfd.io/en/stable/user_guide/analysis.html#warping-analysis for more information.
    warnings.warn(msg, stacklevel=1)
    ```
    - x❌ It does not work for even simple closed wing sections, therefore is not good for my use case.

- `Wing_Full_FE_AeroElas_SourceCode\test_cross_4.py`
    - 🧪 it tests a case with a hollow airfoil section, with two spars at different locations.
    - ✅ good userflow.
    - ✅ it uses `sectionproperties` to compute the cross-section properties, which is a good library for this purpose.
    - ✅ It does not have the "warping" issue for closed wing sections, which is good.
    - ✅ It works very good even for Hollow airfoil sections.
    - ✅ It works very good even for complex airfoil sections, where I have added Two spars at different locations. and I can see the results are correct. and No warnings about warping , therefore there is no issue with the geometry (since the warping issue is related to the geometry, with "The section geometry contains disjoint regions which is invalid for warping analysis."). Therefore, I can say that this is the best test code that works for me.

- `Wing_Full_FE_AeroElas_SourceCode\test_t1.py`
    - 🧪 it tests a case with a closed wing section.
    - ❌ not a very good userflow.
    - ✅ it uses `sectionproperties` to compute the cross-section properties, which is a good library for this purpose.
    - ✅ It does not have the "warping" issue for closed wing sections, which is good.
    - therefore, it is better than the `test_cross_3.py` code, but not as good as the `test_cross_4.py` code.

---

Remember that when I have developed this codebase, I was not good at python programming at all, I had the very basic knowledge of python, and I was not familiar with the libraries used in this codebase, such as `sectionproperties`, `numpy`, `matplotlib`, etc.
Nor was I familiar with the Professional python programming practices, such as modularity, code structure, naming conventions, etc.
Therefore, we can say that across this codebase, there are many issues related to python programming practices, which I have learned over time, that they exist and that they are very important and should not be overlooked.

# Conclusion
We shlould not only focus on my thoughts and observations here, I am sure that there are many other issues that I have not noticed yet, and that should be addressed in the future.