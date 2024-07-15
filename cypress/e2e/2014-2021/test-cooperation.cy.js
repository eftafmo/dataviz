describe("test cooperation", () => {
  it("check cooperation", () => {
    cy.visit("/");
    cy.get("a").contains("Cooperation").click();
    cy.contains("Our Partners");
    cy.contains("Innovation, research, education and competitiveness");
    cy.contains("1 Donor Programme Partner");
  });
});
