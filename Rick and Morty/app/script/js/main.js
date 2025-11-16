document.addEventListener('DOMContentLoaded', () => {
    const loadingOverlay = document.getElementById('loading-overlay');
    const portalOverlay = document.getElementById('portal-overlay');
    const navLinks = document.querySelectorAll('.nav-link');

    // Esconde o loading overlay após a página carregar
    setTimeout(() => {
        loadingOverlay.style.display = 'none';
    }, 800);

    // Efeito de portal ao clicar nos links
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const href = link.href;

            // Anima o portal
            portalOverlay.style.display = 'flex';

            setTimeout(() => {
                window.location.href = href;
            }, 1500); // Aguarda 1.5 segundos antes de redirecionar
        });
    });

    // Esconde o portal ao carregar a página
    window.addEventListener('pageshow', (event) => {
        portalOverlay.style.display = 'none';
        loadingOverlay.style.display = 'none';
    });

    // Efeito de hover nos cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.cursor = 'pointer';
        });
    });

    // Animação de scroll suave
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Efeito de partículas ao fundo (opcional)
    createParticles();
});

// Função para criar partículas animadas de fundo
function createParticles() {
    const particleCount = 30;
    const particles = [];

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.style.position = 'fixed';
        particle.style.width = Math.random() * 5 + 'px';
        particle.style.height = particle.style.width;
        particle.style.backgroundColor = Math.random() > 0.5 ? '#97ce4c' : '#c6ff4d';
        particle.style.borderRadius = '50%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.opacity = Math.random() * 0.5 + 0.1;
        particle.style.zIndex = '-1';
        particle.style.pointerEvents = 'none';

        document.body.appendChild(particle);
        particles.push(particle);

        animateParticle(particle);
    }
}

// Anima as partículas
function animateParticle(particle) {
    const duration = Math.random() * 10 + 5;
    const xMove = Math.random() * 200 - 100;
    const yMove = Math.random() * 200 - 100;

    particle.animate([
        { transform: 'translateX(0) translateY(0)', opacity: Math.random() * 0.5 + 0.1 },
        { transform: `translateX(${xMove}px) translateY(${yMove}px)`, opacity: 0 }
    ], {
        duration: duration * 1000,
        easing: 'ease-in-out'
    });

    // Repete a animação
    setTimeout(() => animateParticle(particle), duration * 1000);
}
