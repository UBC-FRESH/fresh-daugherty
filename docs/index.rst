fresh-daugherty
===============

``fresh-daugherty`` is an open, transparent, and fully reproducible
reproduction of the modelling methods and case study of Daugherty (1991),
using `ws3 <https://github.com/UBC-FRESH/ws3>`_:

   Daugherty, P. J. (1991). *Credibility of Long Term Forest Planning:
   Dynamic Inconsistency in Linear Programming Based Forest Planning Models.*
   PhD thesis, University of California, Berkeley.

Daugherty (1991) proves that linear-programming forest-planning models solved
as **open-loop** formulations admit **dynamically inconsistent** plans — plans
that fail Bellman's principle of optimality, i.e. plans whose tails a future
planner re-solving from the realized state under the same goals would not
follow. Such plans are not a credible basis for policy. The thesis was never
published peer-reviewed and is effectively inaccessible (archival hard copy
only), so the modelling trap it documents is repeatedly rediscovered.

This project reproduces the thesis stack openly so the result becomes citable
and the trap detectable, and it backs a short peer-reviewed paper.

Status: Phase 0 (skeleton scaffold). The master plan lives in
``planning/v0.1.0a1-plan.md``; ``ROADMAP.md`` is the issue-tracker view.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   installation
   quickstart
   development
