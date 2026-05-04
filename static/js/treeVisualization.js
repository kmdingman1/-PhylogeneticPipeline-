// Upload FASTA, fetch /upload, render a rectangular phylogram with d3.
// length from the root (genetic distance), with a small minimum-branch enforcement so short internal branches do not collapse
// If the Newick string has no branch lengths, the renderer falls back to a cladogram (equal leaf depth from d3.cluster).
// Leaves show FASTA IDs; hover reveals species. Click internal nodes to
// Scroll to zoom, drag to pan.

(function () {
    const fileInput = document.getElementById('fileInput');
    const uploadButton = document.getElementById('uploadButton');
    const uploadButtonLabel = document.getElementById('uploadButtonLabel');
    const statusEl = document.getElementById('status');
    const resultsEl = document.getElementById('results');
    const resultsFilename = document.getElementById('resultsFilename');
    const resultsCount = document.getElementById('resultsCount');
    const svgEl = document.getElementById('treeSvg');

    const tooltip = d3.select('body').append('div')
        .attr('class', 'tree-tooltip')
        .style('opacity', 0);

    function setStatus(message, type) {
        statusEl.textContent = message || '';
        statusEl.className = 'status' + (type ? ' status--' + type : '');
    }

    function setBusy(busy) {
        uploadButton.disabled = busy;
        uploadButtonLabel.textContent = busy ? 'Processing...' : 'Upload FASTA File';
    }

    uploadButton.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', async () => {
        const file = fileInput.files && fileInput.files[0];
        if (!file) return;

        resultsEl.hidden = true;
        d3.select(svgEl).selectAll('*').remove();
        setStatus('Uploading ' + file.name + '...');
        setBusy(true);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload', { method: 'POST', body: formData });
            const payload = await response.json().catch(() => ({}));

            if (!response.ok) {
                setStatus(payload.error || 'Upload failed (HTTP ' + response.status + ')', 'error');
                return;
            }

            resultsFilename.textContent = payload.filename || file.name;
            resultsCount.textContent = payload.num_sequences
                ? payload.num_sequences + ' sequences'
                : '';
            resultsEl.hidden = false;
            renderTree(payload.newick, payload.id_to_species || {});
            setStatus('Tree built successfully.', 'success');
        } catch (err) {
            setStatus('Network error: ' + err.message, 'error');
        } finally {
            setBusy(false);
            fileInput.value = '';
        }
    });

    // Newick parser
    // Produces { name, length, children } (children === null for leaves)
    function parseNewick(s) {
        s = s.trim().replace(/;$/, '');
        let pos = 0;

        function parseNode() {
            const node = { name: '', length: 0, children: null };
            if (s[pos] === '(') {
                pos++;
                node.children = [parseNode()];
                while (s[pos] === ',') {
                    pos++;
                    node.children.push(parseNode());
                }
                pos++; // skip ')'
            }
            let name = '';
            while (pos < s.length && ':,)'.indexOf(s[pos]) === -1) name += s[pos++];
            node.name = name;
            if (s[pos] === ':') {
                pos++;
                let len = '';
                while (pos < s.length && ',)'.indexOf(s[pos]) === -1) len += s[pos++];
                node.length = parseFloat(len);
            }
            return node;
        }

        return parseNode();
    }

    // Tree rendering

    function renderTree(newick, idToSpecies) {
        const data = parseNewick(newick);
        const svg = d3.select(svgEl);
        svg.selectAll('*').remove();

        const leafCount = countLeaves(data);
        const rowHeight = 22;
        const margin = { top: 20, right: 220, bottom: 20, left: 40 };
        const containerEl = svgEl.parentNode;
        const width = svgEl.clientWidth || 800;
        const treeHeight = leafCount * rowHeight + margin.top + margin.bottom;
        const height = Math.max(containerEl.clientHeight || 600, treeHeight);
        const innerWidth = width - margin.left - margin.right;
        const innerHeight = height - margin.top - margin.bottom;

        svg.attr('viewBox', `0 0 ${width} ${height}`)
            .attr('width', '100%')
            .attr('height', height);

        const root = d3.hierarchy(data, d => d.children);

        // Cladogram: equal branch lengths (all leaves at same depth)
        const cluster = d3.cluster().size([innerHeight, innerWidth]);

        // Minimum visual branch length, in pixels, so internal branches stay visible and labellable.
        const MIN_BRANCH_PX = 22;

        // Zoom/pan layer
        const zoomLayer = svg.append('g').attr('class', 'zoom-layer');
        const g = zoomLayer.append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        svg.call(
            d3.zoom()
                .scaleExtent([0.2, 8])
                .on('zoom', event => zoomLayer.attr('transform', event.transform))
        );

        const linkGroup = g.append('g').attr('class', 'tree-links');
        const nodeGroup = g.append('g').attr('class', 'tree-nodes');

        update();

        function update() {
            cluster(root);

            // Walk the tree in pre-order and assign each node its cumulative branch length from the root.
            root.eachBefore(d => {
                d.distFromRoot = d.parent
                    ? d.parent.distFromRoot + (d.data.length || 0)
                    : 0;
            });

            // If the Newick string carried any branch lengths, switch the layout from cladogram to phylogram. 
            // Each node's y (horizontal position) becomes proportional to its distance from the root, 
            const maxDist = d3.max(root.descendants(), d => d.distFromRoot) || 0;
            if (maxDist > 0) {
                const xScale = d3.scaleLinear()
                    .domain([0, maxDist])
                    .range([0, innerWidth]);
                root.eachBefore(d => {
                    if (!d.parent) {
                        d.y = 0;
                    } else {
                        const proportional = xScale(d.distFromRoot);
                        const minimum = d.parent.y + MIN_BRANCH_PX;
                        d.y = Math.max(proportional, minimum);
                    }
                });
            }

            const descendants = root.descendants();
            const links = root.links();

            // Right-angle "elbow" paths
            // length is proportional to the child's branch length.
            const linkSel = linkGroup.selectAll('path').data(links, d => keyOf(d.target));
            linkSel.exit().remove();
            linkSel.enter().append('path')
                .attr('class', 'tree-link')
                .merge(linkSel)
                .attr('d', d => `M${d.source.y},${d.source.x}V${d.target.x}H${d.target.y}`);

            // Nodes
            const nodeSel = nodeGroup.selectAll('g.tree-node').data(descendants, keyOf);
            nodeSel.exit().remove();
            const nodeEnter = nodeSel.enter().append('g').attr('class', 'tree-node');
            nodeEnter.append('circle').attr('r', 4);
            nodeEnter.append('text').attr('dy', '0.31em');

            const merged = nodeEnter.merge(nodeSel)
                .attr('transform', d => `translate(${d.y},${d.x})`)
                .classed('leaf', d => !d.children)
                .classed('internal', d => !!d.children);

            // FASTA ID for leaves
            merged.select('text')
                .attr('x', d => d.children ? 0 : 8)
                .attr('text-anchor', 'start')
                .text(d => d.children ? '' : d.data.name);

            // Hover anywhere on a leaf node group: show species tooltip
            merged
                .on('mouseover', (event, d) => {
                    if (d.children) return;                    // only leaves
                    const id = d.data.name;
                    const species = idToSpecies[id] || '(unknown)';
                    tooltip.html(
                        `<strong>${escapeHtml(id)}</strong><br>${escapeHtml(species)}`
                    ).style('opacity', 1);
                    d3.select(event.currentTarget).classed('hovered', true);
                })
                .on('mousemove', event => {
                    tooltip
                        .style('left', (event.pageX + 12) + 'px')
                        .style('top', (event.pageY + 12) + 'px');
                })
                .on('mouseout', event => {
                    tooltip.style('opacity', 0);
                    d3.select(event.currentTarget).classed('hovered', false);
                });
        }
    }

    function keyOf(node) {
        if (!node.__key) node.__key = ++keyOf.counter;
        return node.__key;
    }
    keyOf.counter = 0;

    function countLeaves(n) {
        if (!n.children || n.children.length === 0) return 1;
        return n.children.reduce((sum, c) => sum + countLeaves(c), 0);
    }

    function escapeHtml(s) {
        return String(s).replace(/[&<>"']/g, c => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
        }[c]));
    }
})();
