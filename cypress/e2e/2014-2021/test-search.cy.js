describe("test projects", () => {
  it("check projects", () => {
    cy.visit("/");
    cy.get("form[role=search] input[type=search]").type("programme");
    cy.get("form[role=search]").submit();
    cy.contains("1 programme found");
    cy.contains("Romania");
    cy.contains("Completed");
    cy.contains("Programme 1");
  });
});
