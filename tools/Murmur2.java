// Fingerprint do CurseForge: MurmurHash2 (seed 1) do arquivo sem os bytes 9, 10, 13 e 32.
// Uso: java tools/Murmur2.java arquivo1.jar arquivo2.jar ...   -> imprime "fingerprint<TAB>caminho"
import java.nio.file.*;

public class Murmur2 {
    public static void main(String[] args) throws Exception {
        for (String a : args) {
            byte[] raw = Files.readAllBytes(Path.of(a));
            byte[] d = new byte[raw.length];
            int n = 0;
            for (byte b : raw) if (b != 9 && b != 10 && b != 13 && b != 32) d[n++] = b;
            System.out.println(Integer.toUnsignedString(hash(d, n)) + "\t" + a);
        }
    }

    static int hash(byte[] d, int len) {
        final int m = 0x5bd1e995, r = 24;
        int h = 1 ^ len, i = 0;
        while (len >= 4) {
            int k = (d[i] & 0xff) | (d[i + 1] & 0xff) << 8 | (d[i + 2] & 0xff) << 16 | (d[i + 3] & 0xff) << 24;
            k *= m; k ^= k >>> r; k *= m;
            h *= m; h ^= k;
            i += 4; len -= 4;
        }
        switch (len) {
            case 3: h ^= (d[i + 2] & 0xff) << 16;
            case 2: h ^= (d[i + 1] & 0xff) << 8;
            case 1: h ^= (d[i] & 0xff); h *= m;
        }
        h ^= h >>> 13; h *= m; h ^= h >>> 15;
        return h;
    }
}
