package mercadona;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;
import java.math.BigDecimal;

@Entity
@Table(name = "productos_catalogo")
public class ProductoCatalogo {

    @Id
    @Column(name = "id_producto")
    private String idProducto;

    @Column(name = "nombre_producto")
    private String nombreProducto;

    @Column(name = "categoria")
    private String categoria;

    @Column(name = "precio_venta")
    private BigDecimal precioVenta;

    @Column(name = "coste_proveedor")
    private BigDecimal costeProveedor;

    @Column(name = "stock_actual")
    private int stockActual;

    // Constructor vacío obligatorio para que Hibernate pueda instanciar el objeto
    public ProductoCatalogo() {
    }

    public String getIdProducto() {
        return idProducto;
    }

    public void setIdProducto(String idProducto) {
        this.idProducto = idProducto;
    }

    public String getNombreProducto() {
        return nombreProducto;
    }

    public void setNombreProducto(String nombreProducto) {
        this.nombreProducto = nombreProducto;
    }

    public String getCategoria() {
        return categoria;
    }

    public void setCategoria(String categoria) {
        this.categoria = categoria;
    }

    public BigDecimal getPrecioVenta() {
        return precioVenta;
    }

    public void setPrecioVenta(BigDecimal precioVenta) {
        this.precioVenta = precioVenta;
    }

    public BigDecimal getCosteProveedor() {
        return costeProveedor;
    }

    public void setCosteProveedor(BigDecimal costeProveedor) {
        this.costeProveedor = costeProveedor;
    }

    public int getStockActual() {
        return stockActual;
    }

    public void setStockActual(int stockActual) {
        this.stockActual = stockActual;
    }
}
