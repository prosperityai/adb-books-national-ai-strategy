<!-- Purpose: model clauses for public procurement of AI systems and services.
     Book: National AI Strategy in Practice, Chapter 9. Licence: MIT. -->

# AI Procurement Clauses (Model Text)

Note: model wording only, not legal advice. Counsel must review every
clause against your procurement law and contract standard terms.

Fill the blanks, delete options that do not apply, and keep the clause
numbers so evaluators can cross-refer.

## 1. Definitions

1.1 "Authority Data" means all data supplied by or collected for the
    Authority, and all outputs generated from it.
1.2 "Model" means any machine-learning model supplied, trained or
    fine-tuned under this contract, including its weights.
1.3 "Material Change" means any change to the Model, its training data
    or its hosting that could affect accuracy, fairness or security.

## 2. Data rights

2.1 The Authority owns all Authority Data. The Supplier receives only
    the licence needed to perform this contract.
2.2 The Supplier shall not use Authority Data to train, fine-tune or
    evaluate any model other than for the Authority, unless agreed in
    writing by the Authority.
2.3 Authority Data shall be stored and processed in ____________
    unless the Authority agrees otherwise in writing.
2.4 On request, and at exit, the Supplier returns all Authority Data
    in ____________ format within ____ days and then deletes it,
    certifying deletion in writing.

## 3. Model rights and portability

3.1 Option A (owned): weights of any Model fine-tuned on Authority Data
    belong to the Authority and are delivered every ____ months.
3.2 Option B (licensed): the Authority receives a perpetual licence to
    run the Model on infrastructure of its choice after exit.
3.3 The Supplier shall document the Model (purpose, training data
    sources, evaluation results, known limits) in a model card,
    updated at every Material Change.
3.4 The solution shall use open interfaces listed in Schedule ____ so
    that the Model can be replaced without rebuilding the service.

## 4. Performance and evaluation

4.1 The Supplier meets the accuracy, latency and availability levels
    in Schedule ____, measured on the Authority's test set.
4.2 Performance is reported by group (language, region, sex, age) as
    set out in Schedule ____. Gaps above ____ points are a defect.
4.3 The Authority may run its own tests at any time.
4.4 Service credits for missed levels: ____% of monthly charges per
    level missed, capped at ____%.

## 5. Transparency and audit

5.1 The Supplier keeps logs of inputs, outputs, overrides and Model
    versions for ____ months and gives the Authority access on request.
5.2 The Authority, its auditors and the regulator may audit the
    Supplier's compliance on ____ days' notice.
5.3 The Supplier supports any algorithmic impact assessment and supplies
    the information it needs within ____ days of a request.

## 6. Human oversight

6.1 No decision with legal or similarly significant effect on a person
    is made without review by an Authority officer.
6.2 The system lets officers override outputs, and records each
    override with a reason.

## 7. Change control

7.1 The Supplier notifies the Authority at least ____ days before any
    Material Change and re-runs the tests in clause 4.
7.2 The Authority may refuse a Material Change that lowers performance
    or raises risk.

## 8. Security and incidents

8.1 The Supplier meets the security standard in Schedule ____.
8.2 Security incidents and serious malfunctions are reported to the
    Authority within ____ hours.

## 9. Price and lock-in

9.1 Usage prices (per token, call, user or GPU-hour) are fixed for
    ____ months, then indexed to ____________, capped at ____% a year.
9.2 No minimum commitment beyond ____________ unless stated here.
9.3 Credits or discounts may not be conditional on exclusivity.

## 10. Local capability

10.1 The Supplier trains ____ Authority staff to operate and evaluate
     the system, as set out in Schedule ____.
10.2 Documentation is delivered in ____________ (languages).

## 11. Exit

11.1 An exit plan is delivered within ____ days of signature and kept
     up to date.
11.2 On exit the Supplier provides up to ____ days of transition
     support at the rates in Schedule ____.
11.3 Clauses 2, 3, 5 and 11 survive the end of the contract.

## Evaluation note for the tender panel

Score the bidder's response to clauses 2, 3, 4 and 11 separately.
A bid that rejects clause 2.2 or offers no exit plan should not pass
the technical threshold, whatever its price.
