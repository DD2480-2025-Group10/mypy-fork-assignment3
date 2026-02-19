# Report for assignment 3

This is a template for your report. You are free to modify it as needed.
It is not required to use markdown for your report either, but the report
has to be delivered in a standard, cross-platform format.

## Project

Name:

URL:

One or two sentences describing it

## Onboarding experience

Did it build and run as documented?

See the assignment for details; if everything works out of the box,
there is no need to write much here. If the first project(s) you picked
ended up being unsuitable, you can describe the "onboarding experience"
for each project, along with reason(s) why you changed to a different one.


## Complexity

1. What are your results for five complex functions?
   * Did all methods (tools vs. manual count) get the same result?
   * Are the results clear?
2. Are the functions just complex, or also long?
3. What is the purpose of the functions?
4. Are exceptions taken into account in the given measurements?
5. Is the documentation clear w.r.t. all the possible outcomes?

### `solve_constraints@mypy/solve.py`
Lizard's output for `solve_constraints` in `mypy/solve.py` is as follows:
```
  NLOC    CCN   token  PARAM  length  location
------------------------------------------------
    57     30     423      5      86  solve_constraints@41-126@mypy/solve.py
```

By manually counting the number of `if`, `for` and `else` statements we got a CC of **18**, not matching the 30 reported by Lizard. The difference lies in logical clauses and list comprehensions, which were initially overlooked.

With counting each logical clause (e.g., `and`, `or`) as well as the `for` and `if` statements inside of comprehensions, we arrive at a CC of **30**, matching Lizard's output.

This function in particular is just complex, but not aggressively long. Although 57 lines of code is at the upper end of what should be considered acceptable. Further this function in particular clearly has a lot of different responsibilities (handling three separate boolean flags), which could be a sign that it is possible to reduce its complexity by refactoring those out as separate handlers.

The purpose of the function in to solve type constraints for type variables in the checked program. Which is a core part of the type checking process.

There are no exceptions raised in this function, so they are not taken into account.

The documentation for the function is not very clear. The code is somewhat descriptive but lacks a lot of comments given its complexity and the docstring only gives a very high-level overview. I also feel that the naming of a lot of stuff may be a little to generic, there is a lot of `solve_x`.

**Coverage Results:** Running the test suite with our DIY branch coverage tool shows that **26/26 (92.9%)** of branches are covered by tests. The missing branches are
- Branch 1: `not vars` the function is never called with and empty set of variables.
- Branch 27: `not strict` the function is always tested with strict mode enabled.
For in an in detail view of the results the report can be found [here](https://github.com/DD2480-2025-Group10/mypy-fork-assignment3/pull/19/changes).

#### Refactoring Plan
In order to refactor a function like this, I would first try to identify what is wrong with the current structure, and how impactful the refactoring would be. In this case I begin by noticing that the functions external dependencies are quite few:
- `mypy/subtypes.py:2053`
- `mypy/infer.py:63`
- `mypy/infer.py:76`

Hence I would argue the changing the function signature is alright in this case, although this is not generally the case for functions with a lot of dependants.

Is the signature of the function the issue though? I would argue yes. The function essentially has two modes of solving types depending on if polymorphic functions are allowed or not. Already there the function is conceptually two separate functions. Furthermore, the function handles unsolvable constraints in two different ways depending on the `strict` flag. Once again, this is conceptually two separate functions.

I would argue that in general, passing boolean flags to change the behaviour of a function is significant code smell. What happens if they need to handle one more case? One more flag?

Instead, I would refactor the function into at least two separate concerns:
- Producing solutions for satisfiable variables
- Handling variables that cannot be solved

This introduces a calling order concern, since it seems that we only know what variables cannot be solved after we have attempted to solve the constraints. However, this can be handled by having the second function take as input a typed structure of output from the first function.

Since we produce solutions in separate ways depending on the `allow_polymorphic` flag I would ague that this should be a separate concern as well. The `solve_constraints` function would take as input an interface/strategy for how to solve the constraints and simply apply that strategy to each of the variables. Conceptually it would look something like this:

```
interface ConstraintSolverStrategy:
  ...

class PolymorphicConstraintSolverStrategy(ConstraintSolverStrategy):
  ...

class DefaultConstraintSolverStrategy(ConstraintSolverStrategy):
  ...

struct SolvingResult:
  solved: ...
  unsolved: ...

def solve_constraints(..., strategy: ConstraintSolverStrategy) ->:
  for var in vars:
    solution = strategy.solve(var, var.constraints)
    ...
```

This would dramatically reduce the complexity of the functions and make it much easier to read and maintain. It also makes it easier to add new solving strategies. Furthermore a similar approach can be taken for handling unsolvable constraints.

Lastly, the function does some pre_validation at the end of the function. This is simply a separate concern that should absolutely be factored out into a separate call.

### `is_overlapping_types@mypy/meet.py`
Lizard's output for `is_overlapping_types` in `mypy/meet.py` is as follows:
```
  NLOC    CCN   token  PARAM  length  location
------------------------------------------------
    168     81     1185      6      322  is_overlapping_types@336-657@./mypy/meet.py
```

With counting each logical clause (e.g., `and`, `or`) as well as the `for` and `if` statements inside of comprehensions, we arrive at a CC of **80**, being off by one compared to lizard output. The difference of 1 compared to Lizard’s result is likely due to how the tool counts certain Python-specific constructs, it might count the generator expression for example.

The purpose of is_overlapping_types() is to check whether two mypy types overlap at runtime, meaning whether it is possible for any value to be both left and right. It is used for reachability checks and for verifying whether overload variants or unions might match. Since it must handle many different type categories and each category requires its own branching rules and return paths, it is in my opinion, justified that this function has a high cyclomatic complexity, but some of this logic I think should be moved out into helper function to improve readability.

There are no exceptions or try/catch blocks. The function contains a few asserts for paths that should never occur as sanity checks, but in general it attempts to explicitly handle every case and return early instead of relying on a generic try/catch.

There is quiet a bit of documentation around the different branches.


The quality of our own coverage measurement is quiet limited as it's very annoying to add new paths and requires quiet a bit of boilerplate. This function has no ternary operators or exceptions so that is not applicable here. I did not use an automated tool for this one.

The result of the coverage analyzer was that 49/51 branches were already covered under existing test suite. Of these 3, 2 were unreachable by design so impossible to test. So I added the one test for the branch I could reach and created 3 different tests for path coverage. This was also very difficult to look at the existing test suite and try to figure out if the path had already been covered so I did my best to try and figure it out, but it's almost impossible to actually check on such a large test suite.

### `comparison_type_narrowing_helper@mypy/checker.py`
Lizard's output for `comparison_type_narrowing_helper` in `mypy/checker.py` is as follows:

```
  NLOC    CCN   token  PARAM  length  location
------------------------------------------------
    126     30     618      2      171  comparison_type_narrowing_helper@6452-6622@mypy/checker.py
```

By manually counting the number of decision points (if, elif, logical and/or, and loop constructs) I obtained 29 decision points, resulting in a cyclomatic complexity of 30, which matches Lizard’s output.

Initially, some logical operators inside compound conditions were easy to overlook, but after including each logical clause as a decision point, the manual count aligned with the tool. Therefore, the results are consistent and clear.

This function is both complex and fairly long. With an NLOC of 126 and total length of 171 lines, it is noticeably larger than what is typically considered simple or easy to maintain. The nested conditional structure contributes significantly to the high cyclomatic complexity.

The purpose of comparison_type_narrowing_helper() is to support mypy’s type checker by analyzing comparison expressions (such as x == y, x is y, membership checks, and chained comparisons) and determining how variable types can be narrowed based on the comparison outcome. It returns type maps describing the narrowed types for different execution branches. Because Python comparisons and type relationships are rich and varied, the function must handle many special cases, which largely explains the high complexity.

There are no try/except blocks in this function, so exception handling is not taken into account in the cyclomatic complexity measurement.

The documentation of the function gives a overview of its purpose. However, given the large number of branches and special cases, the documentation does not fully describe all possible outcomes. Understanding the exact behavior in edge cases requires reading the implementation. Additional comments would help.

**Coverage Results**: Running the test suite with our DIY branch coverage tool shows that **13/14 (92.9%)** of branches are covered by tests. The missing branches are
- Branch 2: `not self.has_type`: This branch is unreachable by design because it requires the comparison expression not having a type which will result in errors from mypy's type checking. It functions as defensive code if any upstream code would be wrong. This is probably why this branch isn't tested.

The result of the coverage analysis for comparison_type_narrowing_helper() showed that most branches (13/14) were already exercised by the existing mypy test suite. However, Branch 2 was determined to be unreachable by design, making it impossible to cover through additional tests. I then chose to think about path coverage. To improve coverage, I therefore added two additional tests focused on path coverage, ensuring that different combinations of comparison and membership logic are exercised. Identifying whether particular paths were already covered was challenging due to the size and complexity of the existing test suite.

**Refactoring Plan**: The function comparison_type_narrowing_helper() could be seperated into different helper functions that handle different operators cases:
- `_handle_identity_equality()` — logic for is, is not, ==, != 
- `_handle_membership_comparison()` — logic for in and not in 
- `_apply_optional_narrowing()` — removes None from Optional types when safe 
- `_swap_maps_for_negative_comparison()` — handles negative comparison cases 
- `_fallback_len_narrowing()` — fallback narrowing logic

This would help a lot with readbility of the function aswell as hopefully after refactoring, each helper will have around 5-8 complexity instead of 30.

### `check_return_stmt@mypy/checker.py`
Lizard's output for `check_return_stmt` in `mypy/checker.py` is as follows:
```
  NLOC    CCN   token  PARAM  length  location
------------------------------------------------
    80     33     468      2      110  check_return_stmt@4977-5086@./mypy/checker.py
```


By manually counting decision points including `if`, `elif`, `else`, and logical operators (`and`, `or`), we counted **33 branches**. Using the formula CC = π - s + 2 (with 33 decision points and 7 exit points), we get CC = 33 - 7 + 2 = **28**, which differs from Lizard's **33**.

The discrepancy arises because Lizard counts each branch point individually (including compound conditions with `and`/`or` as separate branches), while the manual calculation using the graph-based formula factors in exit points. Both approaches agree that this function has high complexity.

This function is complex but moderately sized at 80 non-comment lines of code. The complexity comes from handling multiple return statement scenarios: generators, coroutines, async generators, lambdas, typed returns, untyped returns, and various type checking rules (Any, None, UninhabitedType, etc.).

The purpose of `check_return_stmt` is to validate return statements during type checking. It ensures return values match declared return types, handles special cases for generators/coroutines, and reports errors for incompatible returns. This is a critical function in mypy's type checking pipeline.

No exceptions are raised in this function. The function returns early in multiple paths and uses `self.fail()` to report type errors rather than raising exceptions.

The function lacks detailed documentation. There are no comments explaining the complex branching logic, making it difficult to understand the relationships between different checks (e.g., why `UninhabitedType` is checked before expression analysis). A docstring describing the main validation scenarios would improve maintainability.

**Refactoring Plan**: The function could be decomposed into separate helper methods for different return types:
- `_check_generator_return()` for generator-specific logic
- `_check_coroutine_return()` for coroutine handling
- `_check_typed_return()` for expression type checking
- `_check_empty_return()` for empty return statements

This would reduce CC from 33 to approximately 5-8 per function, improving readability while introducing slight overhead from additional function calls.

**Coverage Results**: Running the existing test suite with our DIY branch coverage tool shows **30/33 branches covered (90.9%)**. Three branches remain uncovered:
- Branch 3: `defn is None` - Unreachable as return statements outside functions are syntax errors
- Branch 28: Generator with Any return type + empty return
- Branch 33: Unchecked function with empty return

After adding 4 new test cases targeting uncovered branches, coverage improved to **31/33 (93.9%)**. Branch 28 was successfully covered, but Branch 33 remains difficult to trigger due to mypy's type inference behavior (unannotated functions typically infer `None` or `Any`, bypassing this branch).

## Refactoring

Plan for refactoring complex code:

Estimated impact of refactoring (lower CC, but other drawbacks?).

Carried out refactoring (optional, P+):

git diff ...

## Coverage

### Tools
In the existing codebase, `pytest-cov` was already set up to measure branch coverage. It was not that easy to get it working as it required some special commands line arguments to be passed when running the tests, which was not documented anywhere. But after some trial and error we were able to get it working. Also the measurements of `pytest-cov` are only reported on a per-file basis, therefore to get a more detailed view of coverage for specific functions we had to manually inspect the lines missing coverage.

### Your own coverage tool
To view our own DIY branch coverage tool, view the following diff:
```
git diff 24c4537dc74c2835eb88d36372fcf08c98c76acd^!
```

The tool does only support simple branching structures, i.e not ternary operators or inline branches. This was a bit of a problem when measuring coverage for pythons list comprehensions and generator expressions, which are used quite a lot. But we were able to work around those limitations by manually decomposing such constructs into their expanded forms. In general the tools output was consistent with the results from `pytest-cov`.

### Evaluation

1. How detailed is your coverage measurement?
We would argue that our simple DIY tool is quite detailed in the sense that it measures on a per-function level, rather than just per-file. With proper setup the output is also quite detailed in terms of showing exactly which branches are and are not covered. However, the tool does not support more complex branching structures and also cannot report for example what tests were called to cover a specific branch.

2. What are the limitations of your own tool?
As mentioned above, the tool does not support inline branches such as ternary operators or branches inside of comprehensions. Given that these constructs are common in Python, this is a somewhat significant limitation.

3. Are the results of your tool consistent with existing coverage tools?
The results of our DIY tool are generally consistent with `pytest-cov` if you manually expand inline branching structures. However it can be noted that the DIY tool is manually orchestrated, and hence inconsistencies can arise from human error.

## Coverage improvement

Show the comments that describe the requirements for the coverage.

Report of old coverage: [link]

Report of new coverage: [link]

Test cases added:

git diff ...

Number of test cases added: two per team member (P) or at least four (P+).

# Way of working

## Principles Established

Principles and constraints are committed to by the team. ✅

Principles and constraints are agreed to by the stakeholders. ✅

The tool needs of the work and its stakeholders are agreed.  ✅

A recommendation for the approach to be taken is available. ✅

The context within which the team will operate is understood ✅

The constraints that apply to the selection, acquisition, and use of practices and tools are
known. ✅

## Foundation Established

The key practices and tools that form the foundation of the way-of-working are
selected. ✅

Enough practices for work to start are agreed to by the team. ✅

All non-negotiable practices and tools have been identified. ✅

The gaps that exist between the practices and tools that are needed and the practices and
tools that are available have been analyzed and understood. ✅

The capability gaps that exist between what is needed to execute the desired way of
working and the capability levels of the team have been analyzed and understood. ✅

The selected practices and tools have been integrated to form a usable way-of-working. ✅

## In Use

The practices and tools are being used to do real work. ✅

The use of the practices and tools selected are regularly inspected. ✅

The practices and tools are being adapted to the team’s context. ✅

The use of the practices and tools is supported by the team. ✅

Procedures are in place to handle feedback on the team’s way of working. ✅

The practices and tools support team communication and collaboration. ✅

## In Place

The practices and tools are being used by the whole team to perform their work. ❌

All team members have access to the practices and tools required to do their work. ✅

The whole team is involved in the inspection and adaptation of the way-of-working. ❌


Based on the checklist in the Essence Standard v1.2, we asses our way of working as currently completing the In Use state and starting with the In Place state, having hit 1 milestone in the in place phase. We had some issues with using the same tools in this lab, but in the end we managed to sort it out.

## Overall experience

What are your main take-aways from this project? What did you learn?

Is there something special you want to mention here?
