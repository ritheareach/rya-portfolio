document.getElementById("year").textContent = new Date().getFullYear();

document.documentElement.classList.add("js");
const menuButton = document.querySelector(".menu-toggle");
const navigation = document.getElementById("navigation");

function setMenuOpen(open) {
  menuButton.setAttribute("aria-expanded", String(open));
  menuButton.querySelector(".menu-label").textContent = open ? "Close" : "Menu";
  navigation.classList.toggle("is-open", open);
}

menuButton.addEventListener("click", () => {
  const open = menuButton.getAttribute("aria-expanded") !== "true";
  setMenuOpen(open);
});

navigation.addEventListener("click", (event) => {
  if (event.target.closest("a")) {
    setMenuOpen(false);
  }
});

document.addEventListener("click", (event) => {
  if (!event.target.closest(".site-header")) setMenuOpen(false);
});

window.matchMedia("(max-width: 760px)").addEventListener("change", () => {
  setMenuOpen(false);
});

document.addEventListener("keydown", (event) => {
  if (
    event.key === "Escape" &&
    menuButton.getAttribute("aria-expanded") === "true"
  ) {
    setMenuOpen(false);
    menuButton.focus();
  }
});

document.querySelectorAll("[data-interest]").forEach((link) => {
  link.addEventListener("click", () => {
    sessionStorage.setItem("enquiry-interest", link.dataset.interest);
    const field = document.getElementById("interest");
    if (field) {
      field.value = link.dataset.interest;
      sessionStorage.removeItem("enquiry-interest");
    }
  });
});
const interest = document.getElementById("interest");
if (interest && sessionStorage.getItem("enquiry-interest")) {
  interest.value = sessionStorage.getItem("enquiry-interest");
  sessionStorage.removeItem("enquiry-interest");
}

document.querySelectorAll("img").forEach((image) => {
  image.draggable = false;
});
document.addEventListener("dragstart", (event) => {
  if (event.target.closest("img")) event.preventDefault();
});

async function refreshGalleries() {
  const response = await fetch("assets/image-catalog.json", {
    cache: "no-store",
  });
  if (!response.ok) return;
  const catalog = await response.json();
  const used = new Set(
    [...document.querySelectorAll("img")]
      .filter((image) => !image.closest("#gallery, #robots"))
      .map((image) => image.getAttribute("src")),
  );
  // The hero cutout and this source photograph depict the same robot.
  used.add("assets/robots/005-robot-23.webp");
  for (const [key, sectionId, label] of [
    ["gallery", "gallery", "academy photos"],
    ["robots", "robots", "robot images"],
  ]) {
    const section = document.getElementById(sectionId);
    if (!section) continue;
    const featuredGrid = section.querySelector(":scope > .gallery-grid");
    const featuredCount = featuredGrid.children.length;
    const archive = section.querySelector(".photo-archive");
    const grid = archive.querySelector(".gallery-grid");
    const existing = new Map(
      [...section.querySelectorAll("figure")].map((figure) => [
        figure.querySelector("img").getAttribute("src"),
        figure,
      ]),
    );
    const images = catalog[key].filter((image) => !used.has(image.src));
    const figures = images.map((image) => {
      if (existing.has(image.src)) return existing.get(image.src);
      const figure = document.createElement("figure");
      const frame = document.createElement("div");
      frame.className = "image-frame";
      const img = document.createElement("img");
      img.src = image.src;
      img.alt = image.alt;
      img.loading = "lazy";
      img.draggable = false;
      const caption = document.createElement("figcaption");
      caption.textContent = image.alt;
      frame.append(img);
      figure.append(frame, caption);
      return figure;
    });
    figures.forEach((figure) => figure.classList.remove("gallery-featured"));
    if (sectionId === "gallery" && figures.length) {
      figures[0].classList.add("gallery-featured");
    }
    featuredGrid.replaceChildren(...figures.slice(0, featuredCount));
    grid.replaceChildren(...figures.slice(featuredCount));
    const remaining = Math.max(0, figures.length - featuredCount);
    archive.hidden = remaining === 0;
    const summary = archive.querySelector("summary");
    summary.firstChild.textContent = `Explore ${remaining} more ${label} `;
  }
}
refreshGalleries().catch(() => {
  // Keep the existing galleries usable if the catalog cannot be loaded.
});

document.getElementById("enquiry-form")?.addEventListener("submit", (event) => {
  event.preventDefault();
  const fields = new FormData(event.currentTarget);
  const subject = `RobotYOUNG enquiry: ${fields.get("interest")}`;
  const body = `Name: ${fields.get("name")}\nEmail: ${fields.get("email")}\nInterest: ${fields.get("interest")}\n\n${fields.get("message")}`;
  window.location.href = `https://mail.google.com/mail/?view=cm&fs=1&to=robotyoungacademy%40gmail.com&su=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  document.getElementById("form-status").textContent =
    "Opening Gmail. Sign in if needed, then press Send to send your enquiry.";
});
