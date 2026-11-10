package mercadona;

import org.hibernate.Session;
import org.hibernate.SessionFactory;
import org.hibernate.Transaction;
import org.hibernate.cfg.Configuration;

import java.math.BigDecimal;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * TPI 3 - Ampliación de Bases de Datos (Tema 6)
 * Archivo: java_app/src/main/java/mercadona/AppMercadona.java
 * Propósito: Demostrar en una misma aplicación sencilla:
 *   1. Acceso mediante JDBC con buenas prácticas (try-with-resources,
 *      PreparedStatement parametrizado contra SQL Injection y Transacción ACID).
 *   2. Acceso mediante ORM Hibernate trabajando directamente con objetos Java
 *      (ProductoCatalogo) y consultas HQL parametrizadas.
 */
public class AppMercadona {

    private static final String URL_JDBC = "jdbc:postgresql://mercadona_postgres:5432/mercadona_bi";
    private static final String USUARIO = "postgres";
    private static final String CLAVE = "postgres";

    public static void main(String[] args) {
        // Ocultamos los avisos internos de arranque de Hibernate para ver la salida limpia
        Logger.getLogger("org.hibernate").setLevel(Level.OFF);

        probarAccesoJDBC();
        System.out.println();
        probarAccesoHibernate();
    }

    /**
     * PARTE 1: Interfaz JDBC + Buenas Prácticas (PreparedStatement + Transacción ACID)
     */
    private static void probarAccesoJDBC() {
        System.out.println("======================================================================");
        System.out.println(" 1. ACCESO MEDIANTE JDBC Y BUENAS PRÁCTICAS (PostgreSQL)");
        System.out.println("======================================================================");

        // Buena práctica 1: try-with-resources para cerrar siempre la conexión automáticamente
        try (Connection conn = DriverManager.getConnection(URL_JDBC, USUARIO, CLAVE)) {
            System.out.println("[OK] Conexión JDBC abierta con éxito hacia 'mercadona_bi'.\n");

            // Buena práctica 2: Consulta parametrizada (?) con PreparedStatement contra SQL Injection
            String sqlVista = "SELECT franja_horaria, nombre_producto, unidades_totales, "
                            + "precio_venta, coste_proveedor, beneficio_neto_tramo_eur "
                            + "FROM vista_direccion_mercadona "
                            + "WHERE beneficio_neto_tramo_eur >= ? "
                            + "ORDER BY franja_horaria";

            try (PreparedStatement ps = conn.prepareStatement(sqlVista)) {
                ps.setBigDecimal(1, new BigDecimal("500.00")); // Filtramos tramos con beneficio >= 500 €

                try (ResultSet rs = ps.executeQuery()) {
                    System.out.println("--- Consulta Nivel Externo Dirección (Beneficio neto >= 500 €) ---");
                    System.out.printf("%-8s | %-30s | %-6s | %-7s | %-7s | %-10s%n",
                            "Franja", "Producto", "Uds.", "Venta", "Coste", "Beneficio");
                    System.out.println("--------------------------------------------------------------------------------");
                    while (rs.next()) {
                        System.out.printf("%-8s | %-30s | %6d | %5.2f € | %5.2f € | %8.2f €%n",
                                rs.getString("franja_horaria"),
                                rs.getString("nombre_producto"),
                                rs.getLong("unidades_totales"),
                                rs.getBigDecimal("precio_venta"),
                                rs.getBigDecimal("coste_proveedor"),
                                rs.getBigDecimal("beneficio_neto_tramo_eur"));
                    }
                }
            }

            // Buena práctica 3: Gestión manual de transacciones ACID (commit / rollback)
            System.out.println("\n--- Transacción ACID en JDBC: Registro de pedido de reposición ---");
            conn.setAutoCommit(false);
            String sqlInsert = "INSERT INTO reposiciones_stock (id_tienda, id_producto, unidades_reponer, franja_horaria) "
                             + "VALUES (?, ?, ?, ?)";
            try (PreparedStatement psInsert = conn.prepareStatement(sqlInsert)) {
                psInsert.setString(1, "MERC_SEV_TRIANA");
                psInsert.setString(2, "PROD_05");
                psInsert.setInt(3, 100);
                psInsert.setString(4, "12:00");
                psInsert.executeUpdate();

                conn.commit();
                System.out.println("[COMMIT] Pedido de 100 uds. de PROD_05 registrado en MERC_SEV_TRIANA.");
            } catch (Exception e) {
                conn.rollback();
                System.out.println("[ROLLBACK] Error en la transacción, cambios deshechos: " + e.getMessage());
            }

        } catch (Exception e) {
            System.err.println("Error general en JDBC: " + e.getMessage());
        }
    }

    /**
     * PARTE 2: Uso de ORM Hibernate (Mapeo Objeto-Relacional de ProductoCatalogo)
     */
    private static void probarAccesoHibernate() {
        System.out.println("======================================================================");
        System.out.println(" 2. ACCESO MEDIANTE ORM HIBERNATE (Entidad ProductoCatalogo)");
        System.out.println("======================================================================");

        // Inicializamos SessionFactory leyendo hibernate.cfg.xml y cerrándola con try-with-resources
        try (SessionFactory factory = new Configuration().configure("hibernate.cfg.xml").buildSessionFactory();
             Session session = factory.openSession()) {

            // A) Recuperar una fila como objeto Java por su clave primaria (sin escribir SQL)
            System.out.println("--- A) Búsqueda directa de objeto con session.get() ---");
            ProductoCatalogo prod = session.get(ProductoCatalogo.class, "PROD_05");
            System.out.println("Objeto cargado en Java -> ID: " + prod.getIdProducto()
                    + " | Nombre: " + prod.getNombreProducto()
                    + " | Precio: " + prod.getPrecioVenta() + " €"
                    + " | Stock antes: " + prod.getStockActual());

            // B) Modificar el objeto en Java y guardar cambios automáticamente con una transacción ORM
            System.out.println("\n--- B) Actualización de stock modificando el objeto Java ---");
            Transaction tx = session.beginTransaction();
            prod.setStockActual(prod.getStockActual() + 50); // Sumamos 50 packs al stock
            tx.commit(); // Hibernate detecta el cambio y lanza el UPDATE automáticamente
            System.out.println("Stock actualizado en PostgreSQL mediante ORM -> Stock ahora: " + prod.getStockActual());

            // C) Consulta HQL orientada a objetos y parametrizada (:cat)
            System.out.println("\n--- C) Consulta HQL sobre objetos de la categoría 'Lácteos' ---");
            List<ProductoCatalogo> lacteos = session.createQuery(
                    "FROM ProductoCatalogo p WHERE p.categoria = :cat", ProductoCatalogo.class)
                    .setParameter("cat", "Lácteos")
                    .getResultList();

            for (ProductoCatalogo l : lacteos) {
                System.out.println("  * " + l.getIdProducto() + " - " + l.getNombreProducto()
                        + " (" + l.getPrecioVenta() + " €, Stock: " + l.getStockActual() + ")");
            }
        }
    }
}
