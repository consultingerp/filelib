12.0.3.1.0 (2019-12-17)
~~~~~~~~~~~~~~~~~~~~~~~

**Features**

- Handle multi currency for account analytic view. The amount in this
  view are now converted to the base currency (the one with rate 1),
  so summing them has some meaning. As a consequence, this view has
  less usefulness if the company currency is not the one with rate 1,
  Debit and credit being assumed to be in company currency.

  Add the M2M to account.analytic.tag in the account analytic view.

  Fix sign issue in account analytic view.


  These are breaking changes. Change the status of ``mis_builder_demo`` to alpha,
  since it is a demo module and it's content can change at any time without
  any compatibility guarantees. (`#222 <https://github.com/oca/mis-builder/issues/222>`_)


**Bugfixes**

- Fix date casting error on committed expenses drilldown. (`#185 <https://github.com/oca/mis-builder/issues/185>`_)
