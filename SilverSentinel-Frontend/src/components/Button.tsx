import { cva } from "class-variance-authority";
import { twMerge } from "tailwind-merge";

const buttonStyles = cva(
    "h-12 border rounded-full px-6 font-medium inline-flex items-center justify-center",
    {
        variants: {
            variant: {
                primary: "bg-lime-400 text-neutral-950 border-lime-400",
                secondary: "border-white text-white bg-transparent",
            },
            size: {
                sm: "h-10",
                lg: "h-14",
            }
        },
        defaultVariants: {
            variant: "primary",
        },
    }
);

export default function Button(
    props: React.ButtonHTMLAttributes<HTMLButtonElement> & {
        variant: "primary" | "secondary";
        size?: "sm" | "lg";
    }
) {
    const { variant, className, size, ...otherProps } = props;
    return (
        <button
            className={twMerge(buttonStyles({ variant, size }), className)}
            {...otherProps}
        />
    );
}
