Feature: Test


@tag
  Scenario Outline: aa
    Given a
      And aa
      And daf
    When aaa
      And aaa
        | 1 11 | 12ffff   ffff | 13 f |
        |      | 22            | 23   |
    Then ff
      And sgs
    Examples:
      | 1 11 | 12ffff   ffff | 13 f |
      | 21   | 22            | 23   |
      | 311  |               |      |


@tagf s sg rsgr
  Scenario: aa
    Given a
      And aa
      And daf
    When aaa
      And aaa
        | 1 11 | 12ffff   ffff | 13 f |
        |      | 22            | 23   |
    Then ff
      And sgs
