describe("test funding", () => {
  it("check funding", () => {
    cy.visit("/");
    cy.get("a").contains("Funding").click();
    cy.contains("Funding by Financial Mechanism 2014-2021");
    cy.contains("Innovation, research, education and competitiveness");
    cy.contains("€32,000 gross allocation");
    cy.get(".indicator")
      .first()
      .should("contain", "50,000")
      .and("contain", "Indicator 1");
  });
});
