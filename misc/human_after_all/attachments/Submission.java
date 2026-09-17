public final class Submission {
    private static int clamp(int value) {
        int result = Math.max(0, Math.min(value, 100));
        return result;
    }

    public static void main(String[] args) {
        int value = args.length == 0 ? 23 : Integer.parseInt(args[0]);
        int result = clamp(value * 2 + 1);
        System.out.println("Result: " + result);
    }
}

/*{{NOTE}}*/
