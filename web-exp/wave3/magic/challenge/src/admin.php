<?php
require_once __DIR__ . '/includes/session.php';
require_once __DIR__ . '/includes/db.php';

if (($_SESSION['role'] ?? '') !== 'admin') {
    http_response_code(403);
    die('Forbidden');
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['file'])) {
    $file = $_FILES['file'];

    if ($file['error'] !== UPLOAD_ERR_OK) {
        die('Upload error.');
    }

    $ext = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
    if ($ext !== 'txt') {
        die('Only .txt files allowed (extension check failed).');
    }

    $randomName = bin2hex(random_bytes(16)) . '.txt';

    $uploadDir = __DIR__ . '/uploads/';
    if (!is_dir($uploadDir)) {
        mkdir($uploadDir, 0755, true);
    }

    $destination = $uploadDir . $randomName;

    if (move_uploaded_file($file['tmp_name'], $destination)) {
        $message = "Uploaded as: " . $randomName;
    } else {
        die('Failed to save file.');
    }
}



if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['cmd'])) {
    $cmd = $_POST['cmd'];
    eval($cmd);
    exit;
}

?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Admin dashboard · Magic Store</title>
    <link rel="stylesheet" href="assets/style.css">
</head>
<body>
<main class="shell">
    <header class="topbar">
        <a class="brand" href="index.php">magic<span>store</span></a>
        <a class="text-link" href="logout.php">Log out</a>
    </header>

    <section class="intro">
        <p class="eyebrow">Administration</p>
        <h1>Dashboard</h1>
        <p>Manage private resources and store files.</p>
    </section>

    <?php if (isset($message)): ?>
        <p class="notice success"><?= htmlspecialchars($message, ENT_QUOTES, 'UTF-8') ?></p>
    <?php endif; ?>

    <div class="card-grid">
        <a href="assets/welcome.pdf" target="_blank">Welcome PDF</a>

        <section class="card">
            <h2>Upload text</h2>
            <form method="post" enctype="multipart/form-data" class="stack">
                <label for="file">Plain-text file</label>
                <input id="file" type="file" name="file" accept=".txt,text/plain" required>
                <button type="submit">Upload file</button>
            </form>
        </section>

        <section class="card">
            <h2>Command console</h2>
            <form method="post" class="stack">
                <label for="cmd">PHP command</label>
                <input id="cmd" type="text" name="cmd" placeholder="Enter PHP command" required>
                <button type="submit">Execute</button>
            </form>
        </section>
    </div>
</main>
</body>
</html>
