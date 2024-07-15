describe("test projects", () => {
  it("check projects", () => {
    cy.visit("/");
    cy.get("a").contains("Projects").click();
    cy.contains("Innovation, research, education and competitiveness");
    cy.contains("The news hasn't happened yet");
    cy.contains("€32,000");
  });
});
