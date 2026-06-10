package com.jk.labs.vkp.datacollection.service.snapshot;

/** Parses a {@code vkp.snapshot.location} value into (bucket/container, prefix) for the cloud stores. */
public final class SnapshotLocations {

    private SnapshotLocations() {
    }

    /**
     * {@code 's3://bucket/prefix'} | {@code 'gs://bucket/prefix'} | {@code 'bucket/prefix'} | {@code 'bucket'}
     * → {@code [bucket, prefix]} where prefix is "" or ends with "/".
     */
    public static String[] bucketPrefix(String location, String scheme) {
        if (location == null || location.isBlank()) {
            throw new IllegalStateException("vkp.snapshot.location is required for the '" + scheme
                    + "' backend (e.g. '" + scheme + "://my-bucket/vkp-snapshots').");
        }
        String s = location.trim();
        for (String p : new String[]{scheme + "://", "s3://", "gs://"}) {
            if (s.startsWith(p)) {
                s = s.substring(p.length());
                break;
            }
        }
        s = strip(s);
        int slash = s.indexOf('/');
        if (slash < 0) {
            return new String[]{s, ""};
        }
        String bucket = s.substring(0, slash);
        String prefix = strip(s.substring(slash + 1));
        return new String[]{bucket, prefix.isEmpty() ? "" : prefix + "/"};
    }

    /** {@code 'container'} | {@code 'container/prefix'} → {@code [container, prefix]} (prefix "" or ends "/"). */
    public static String[] containerPrefix(String location) {
        if (location == null || location.isBlank()) {
            throw new IllegalStateException("vkp.snapshot.location is required for the 'azure' backend "
                    + "(e.g. 'my-container' or 'my-container/vkp-snapshots').");
        }
        return bucketPrefix(location, "azure");
    }

    private static String strip(String s) {
        int a = 0;
        int b = s.length();
        while (a < b && s.charAt(a) == '/') {
            a++;
        }
        while (b > a && s.charAt(b - 1) == '/') {
            b--;
        }
        return s.substring(a, b);
    }
}
