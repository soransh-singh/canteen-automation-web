import { withStyles } from "@material-ui/core/styles";
import Button from "@material-ui/core/Button";

const styles = (theme) => ({
    root: {
        color: "#0477BD",
        margin: theme.spacing.unit,
    },
});

export default withStyles(styles)(Button);
