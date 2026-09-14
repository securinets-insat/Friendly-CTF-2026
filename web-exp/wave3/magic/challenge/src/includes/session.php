<?php
session_start([
    'cookie_httponly' => true,
    'cookie_samesite' => 'Strict',
]);
if (!isset($_SESSION['role'])) {
    $_SESSION['role'] = 'guest';
}

function isAdmin(): bool {
    return ($_SESSION['role'] ?? 'guest') === 'admin';
}
