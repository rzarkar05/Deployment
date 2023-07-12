showProjectContent(1);
startSlideshow();
var slides = document.querySelectorAll(".slide");
var currentSlide = 0;

function showSlide(index) {
    // Remove active class from all slides
    for (var i = 0; i < slides.length; i++) {
        slides[i].classList.remove("active");
    }
    
    // Add active class to the current slide
    slides[index].classList.add("active");

}

function nextSlide() {
    currentSlide = (currentSlide + 1) % slides.length;
    showSlide(currentSlide);
    
}
var slideshowInterval; // Global variable to store the interval ID

function startSlideshow() {
slideshowInterval = setInterval(nextSlide, 3000); // Start the slideshow with a 3-second interval
}

function stopSlideshow() {
clearInterval(slideshowInterval); // Stop the slideshow by clearing the interval
}

// Example button click event handler
var button = document.getElementById("slideshowButton");

button.addEventListener("click", function() {
if (button.textContent === "Pause") {
    stopSlideshow(); // Call the stopSlideshow function
    button.textContent = "Resume";
} else {
    startSlideshow(); // Call the startSlideshow function
    button.textContent = "Pause";
}
});


function showProjectContent(projectNumber) {
    // Hide all project details
    var projectDetails = document.getElementsByClassName("project-details");
    for (var i = 0; i < projectDetails.length; i++) {
        projectDetails[i].style.display = "none";
    }

    // Show the selected project's content
    var selectedProject = document.getElementById("project" + projectNumber);
    selectedProject.style.display = "block";
}



$(document).ready(function () {
    $(window).scroll(function () {
        if (this.scrollY > 20) {
            $(".navbar").addClass("sticky");
        } else {
            $(".navbar").removeClass("sticky");
        }
    });
    $('.menu-btn').click(function(){
        $('.navbar .menu').toggleClass("active");
        $('.menu-btn i').toggleClass("active");
    });

    // typing animation script
    var typed = new Typed(".typing",{
        strings: ["Student","Developer","Innovator"],
        typeSpeed: 100,
        backSpeed: 60,
        loop: true,
        fadeOut: true, 
    });
    var typed = new Typed(".typing-2",{
        strings: ["Student","Developer","Innovator"],
        typeSpeed: 100,
        backSpeed: 60,
        loop: true,
    });
});

// Scroll to top button script
const btnScrollToTop = document.querySelector("#btnScrollToTop");
btnScrollToTop.addEventListener("click", function(){
    window.scrollTo({
    top: 0,
    left: 0,
    behavior: "smooth"
    });
});