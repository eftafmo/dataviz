describe("test projects", () => {
  it("check projects", () => {
    cy.visit("/");
    cy.get("a").contains("Global Goals").click();
    cy.get(".indicator")
      .first()
      .should("contain", "50,000")
      .and("contain", "Indicator 1");
    cy.contains("€42,000");
    cy.contains("Life on land");
  });
});
