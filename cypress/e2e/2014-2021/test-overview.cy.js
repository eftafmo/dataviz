describe("test overview", () => {
  it("check overview", () => {
    cy.visit("/");
    cy.contains("€32 K");
  });
});
