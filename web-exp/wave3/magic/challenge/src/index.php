<?php
session_start();
require 'includes/db.php';

$products = $productsCollection->find(
    [],
    ['projection' => ['_id' => 0, 'name' => 1, 'price' => 1]]
);
$searchTerm = '';

if ($_SERVER['REQUEST_METHOD'] === 'GET' && isset($_GET['name']) && trim((string) $_GET['name']) !== '') {
    $searchTerm = trim((string) $_GET['name']);
    $filter = ['name' => $searchTerm];
    $products = $productsCollection->find(
        $filter,
        ['projection' => ['_id' => 0, 'name' => 1, 'price' => 1]]
    );
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['name'])) {
    $filter = $_POST ?: [];
    $products = $productsCollection->find(
        $filter,
        ['projection' => ['_id' => 0, 'name' => 1, 'price' => 1]]
    );
    $jsonProducts = json_encode(iterator_to_array($products));
    header('Content-Type: application/json');
    echo $jsonProducts;
    exit;
}

?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Magic Store</title>
    <link rel="stylesheet" href="assets/style.css">
</head>
<body>
<main class="shell">
    <header class="topbar">
        <a class="brand" href="index.php">magic<span>store</span></a>
        <a class="text-link" href="admin_login.php">Admin</a>
    </header>

    <section class="hero">
        <p class="eyebrow">Simple technology, thoughtfully selected</p>
        <h1>Find what works<br>beautifully.</h1>
        <p>Search our compact collection of everyday essentials.</p>

        <form method="get" class="search-form">
            <label class="sr-only" for="name">Product name</label>
            <input
                id="name"
                type="search"
                name="name"
                placeholder="e.g. Wireless Mouse"
                value="<?= htmlspecialchars($searchTerm, ENT_QUOTES, 'UTF-8') ?>"
            >
            <button type="submit">Search</button>
        </form>
    </section>

    <section class="results" aria-live="polite">
        <?php if ($searchTerm !== ''): ?>
            <h2>Search results</h2>
        <?php endif; ?>
        <?php $foundProducts = iterator_to_array($products); ?>

        <?php if ($foundProducts): ?>
            <div class="product-grid">
                <?php foreach ($foundProducts as $product): ?>
                    <article class="product-card">
                        <h3><?= htmlspecialchars((string) $product['name'], ENT_QUOTES, 'UTF-8') ?></h3>
                        <p>$<?= number_format((float) $product['price'], 2) ?></p>
                    </article>
                <?php endforeach; ?>
            </div>
        <?php else: ?>
            <p class="empty">No products matched that name.</p>
        <?php endif; ?>
    </section>
</main>
</body>
</html>
