window.MathJax = {
    tex: {
	    inlineMath: [['$', '$'], ['\\(', '\\)']],
        // packages: {'[+]' : ['blkarray']}
    },
    svg: {
        fontCache: 'global'
      },
    processEnvironments: true,
};

//simply autoimport so the config and import of mathJax are handled in a single file, you can import it as async
// in the html since it doesn't depend on other scripts now
(function () {
  let script = document.createElement('script');
  script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js';
  script.async = true;
  document.head.appendChild(script);
})();
