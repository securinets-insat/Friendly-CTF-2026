<?php
require_once __DIR__ . '/includes/session.php';
require_once __DIR__ . '/includes/db.php';
if (isAdmin()) {
    header('Location: admin.php');
    exit;
}


if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['secret'])) {
    $hash = hash('sha1', $_POST['secret']);
    $secret_hash = $settingsCollection->findOne(['key' => 'secret_hash'])['value'] ?? '';
    if ($secret_hash == $hash) {
        $_SESSION['role'] = 'admin';
        header('Location: admin.php');
        exit;
    } else {
        http_response_code(403);
        $error = 'Invalid secret key.';
    }
}

?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Admin login · Magic Store</title>
    <link rel="stylesheet" href="assets/style.css">
</head>
<body>
<main class="shell narrow">
    <header class="topbar">
        <a class="brand" href="index.php">magic<span>store</span></a>
    </header>

    <section class="auth-card">
        <p class="eyebrow">Restricted area</p>
        <h1>Admin sign in</h1>
        <p>Enter the administrator secret to continue.</p>

        <?php if (isset($error)): ?>
            <p class="notice error" role="alert">
                <?= htmlspecialchars($error, ENT_QUOTES, 'UTF-8') ?>
            </p>
        <?php endif; ?>

        <form method="post" action="admin_login.php" class="stack">
            <label for="secret">Admin secret</label>
            <input
                id="secret"
                type="password"
                name="secret"
                autocomplete="current-password"
                required
                autofocus
            >
            <button type="submit">Enter dashboard</button>
        </form>
    </section>
</main>
</body>
</html>
